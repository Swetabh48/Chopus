import dotenv from "dotenv";
import fs from "fs";
import path from "path";
import { PrismaLibSql } from "@prisma/adapter-libsql";
import { PrismaClient } from "../generated/prisma/client.ts";

dotenv.config({
  path: path.resolve(import.meta.dirname, "../../../.env"),
  override: true,
});

const defaultDbFile = path.resolve(import.meta.dirname, "../data/chopus.db");
const rawUrl = process.env.DATABASE_URL?.trim();
const databaseUrl =
  rawUrl && rawUrl !== "undefined" && !rawUrl.startsWith("postgres")
    ? rawUrl
    : `file:${defaultDbFile}`;

if (!databaseUrl.startsWith("file:")) {
  throw new Error(
    `Local PrivateGPT expects a SQLite DATABASE_URL (file:...), got: ${databaseUrl}`,
  );
}

const filePath = databaseUrl.replace(/^file:/, "");
fs.mkdirSync(path.dirname(filePath), { recursive: true });

const adapter = new PrismaLibSql({ url: databaseUrl });

export const db = new PrismaClient({ adapter });
