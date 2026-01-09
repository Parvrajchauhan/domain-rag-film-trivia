import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const body = await req.json();

    const backendRes = await fetch(
      process.env.BACKEND_URL || "http://localhost:8000/query",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      }
    );

    if (!backendRes.ok) {
      const text = await backendRes.text();
      return NextResponse.json(
        { error: "Backend error", details: text },
        { status: backendRes.status }
      );
    }

    
    const data = await backendRes.json();
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json(
      { error: "Internal API error", details: err.message },
      { status: 500 }
    );
  }
}
