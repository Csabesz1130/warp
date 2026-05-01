import { NextResponse } from "next/server";
import { overview } from "@/lib/mockData";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(overview());
}
