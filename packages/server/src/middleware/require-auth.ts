import { createMiddleware } from "hono/factory";
import { authenticateOAuthRequest } from "../lib/auth";
import { isLocalMode, LOCAL_USER_ID } from "../lib/local-mode";

export type AuthenticatedEnv = {
  Variables: {
    userId: string;
  };
};

export const requireAuth = createMiddleware<AuthenticatedEnv>(async (c, next) => {
  if (isLocalMode()) {
    c.set("userId", LOCAL_USER_ID);
    await next();
    return;
  }

  try {
    const auth = await authenticateOAuthRequest(c.req.raw);
    if (!auth) {
      return c.json({ error: "Unauthorized. Run /login to continue." }, 401);
    }

    c.set("userId", auth.userId);
    await next();
  } catch {
    return c.json({ error: "Unauthorized. Run /login to continue." }, 401);
  }
});
