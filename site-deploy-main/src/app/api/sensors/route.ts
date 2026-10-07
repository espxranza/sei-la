import { NextRequest, NextResponse } from "next/server";

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const INGEST_API_KEY = process.env.INGEST_API_KEY;

function configError() {
  return NextResponse.json({ error: "API não configurada." }, { status: 500 });
}

async function supabaseFetch(path: string, init: RequestInit = {}) {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) return null;
  return fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    ...init,
    headers: {
      apikey: SUPABASE_SERVICE_ROLE_KEY,
      Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
      "Content-Type": "application/json",
      ...(init.headers || {}),
    },
    cache: "no-store",
  });
}

export async function GET(request: NextRequest) {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY || !INGEST_API_KEY) return configError();
  const limit = Math.min(Math.max(Number(request.nextUrl.searchParams.get("limit") || "288"), 1), 1000);
  const response = await supabaseFetch(
    `sensor_readings?select=id,timestamp,temperature,humidity,wind_kmh,uv,pressure_hpa&order=timestamp.desc&limit=${limit}`
  );
  if (!response || !response.ok) return NextResponse.json({ error: "Falha ao consultar dados." }, { status: 502 });
  return NextResponse.json(await response.json());
}

export async function POST(request: NextRequest) {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY || !INGEST_API_KEY) return configError();
  if (request.headers.get("x-api-key") !== INGEST_API_KEY) {
    return NextResponse.json({ error: "Não autorizado." }, { status: 401 });
  }
  try {
    const body = await request.json();
    const values = {
      timestamp: body.timestamp || new Date().toISOString(),
      temperature: Number(body.temperature),
      humidity: Number(body.humidity),
      wind_kmh: Number(body.wind_kmh),
      uv: Number(body.uv),
      pressure_hpa: Number(body.pressure_hpa),
    };
    if (Object.values(values).slice(1).some((v) => !Number.isFinite(v))) {
      return NextResponse.json({ error: "Dados inválidos." }, { status: 400 });
    }
    const response = await supabaseFetch("sensor_readings", {
      method: "POST",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify(values),
    });
    if (!response || !response.ok) return NextResponse.json({ error: "Falha ao salvar leitura." }, { status: 502 });
    return NextResponse.json({ ok: true });
  } catch {
    return NextResponse.json({ error: "JSON inválido." }, { status: 400 });
  }
}
