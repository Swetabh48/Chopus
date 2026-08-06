import { createClerkClient } from "@clerk/backend";
import { isLocalMode, LOCAL_USER_ID } from "./local-mode";

const clerkClient =
  !isLocalMode() &&
  process.env.CLERK_SECRET_KEY &&
  process.env.CLERK_PUBLISHABLE_KEY
    ? createClerkClient({
        secretKey: process.env.CLERK_SECRET_KEY,
        publishableKey: process.env.CLERK_PUBLISHABLE_KEY,
      })
    : null;

if (!isLocalMode() && !clerkClient) {
  throw new Error(
    "CLERK_SECRET_KEY and CLERK_PUBLISHABLE_KEY are required unless LOCAL_MODE=true",
  );
}

export async function authenticateOAuthRequest(request: Request) {
  if (isLocalMode()) {
    return { userId: LOCAL_USER_ID };
  }

  if (!clerkClient) {
    return null;
  }

  const requestState = await clerkClient.authenticateRequest(request, {
    acceptsToken: "oauth_token",
  });

  if (!requestState.isAuthenticated) {
    return null;
  }

  const auth = requestState.toAuth();
  if (auth.tokenType !== "oauth_token" || !auth.userId) {
    return null;
  }

  return { userId: auth.userId };
}
