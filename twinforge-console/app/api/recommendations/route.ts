import { NextResponse } from "next/server";
import { recommendations } from "@/lib/mockData";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json({ recommendations: recommendations() });
}

export async function POST(req: Request) {
  const body = (await req.json()) as { id?: string; action?: "approve" | "reject" };
  if (!body.id || !body.action) {
    return NextResponse.json({ error: "id and action required" }, { status: 400 });
  }
  return NextResponse.json({
    id: body.id,
    status: body.action === "approve" ? "approved" : "rejected",
    appliedAt: body.action === "approve" ? new Date().toISOString() : null,
  });
}
