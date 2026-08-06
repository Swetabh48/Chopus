/**
 * PrivateGPT default: fully local, no Clerk signup.
 * Set LOCAL_MODE=false only if you intentionally want cloud auth.
 */
export function isLocalMode() {
  return process.env.LOCAL_MODE !== "false";
}

export const LOCAL_USER_ID = "local-user";
