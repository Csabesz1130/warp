import { NextResponse } from "next/server";
import { savingsReport } from "@/lib/mockData";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(savingsReport());
}
