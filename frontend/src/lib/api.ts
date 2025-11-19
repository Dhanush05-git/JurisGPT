export const BACKEND_URL = "http://127.0.0.1:8000";

export async function askJurisGPT(query: string) {
  try {
    const res = await fetch(`${BACKEND_URL}/api/query/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });

    if (!res.ok) {
      throw new Error("Backend error");
    }

    return res.json();
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
}