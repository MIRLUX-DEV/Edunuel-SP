const KV_KEY = "horoscope";

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}

async function readStaticFallback(request) {
  const url = new URL("/data/horoscopo.json", request.url);
  const res = await fetch(url.toString(), { cf: { cacheTtl: 0 } });
  if (!res.ok) return null;
  return res.json();
}

export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);

  if (url.searchParams.has("check")) {
    return jsonResponse({
      ok: true,
      writable: !!env.HOROSCOPE_KV,
    });
  }

  if (env.HOROSCOPE_KV) {
    const stored = await env.HOROSCOPE_KV.get(KV_KEY, "json");
    if (stored) return jsonResponse(stored);
  }

  const fallback = await readStaticFallback(request);
  if (fallback) return jsonResponse(fallback);

  return jsonResponse({ error: "Horóscopo no disponible" }, 404);
}

export async function onRequestPost(context) {
  const { request, env } = context;

  if (!env.HOROSCOPE_KV) {
    return jsonResponse(
      { error: "Almacenamiento no configurado en el hosting (KV)" },
      503,
    );
  }

  const pin = request.headers.get("X-Admin-Pin") || "";
  const expected = env.ADMIN_PIN || "edunuel2026";
  if (pin !== expected) {
    return jsonResponse({ error: "PIN incorrecto" }, 403);
  }

  let data;
  try {
    data = await request.json();
    if (!Array.isArray(data.signs) || data.signs.length === 0) {
      throw new Error("JSON inválido");
    }
  } catch {
    return jsonResponse({ error: "JSON inválido" }, 400);
  }

  await env.HOROSCOPE_KV.put(KV_KEY, JSON.stringify(data));
  return jsonResponse({ ok: true, updated: data.updated || null });
}
