"use client";

import React, { useEffect, useState } from "react";

type Version = {
  id: string;
  name: string;
  status: string;
  created_at: string;
};

export default function AdminDashboard() {
  const API = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000";

  const [files, setFiles] = useState<File[] | null>(null);
  const [versions, setVersions] = useState<Version[]>([]);
  const [loading, setLoading] = useState(false);
  const [log, setLog] = useState<string>("");

  useEffect(() => {
    fetchVersions();
  }, []);

  async function fetchVersions() {
    try {
      const res = await fetch(`${API}/admin/versions`);
      if (!res.ok) throw new Error("Failed to fetch versions");
      const data = await res.json();
      setVersions(data.versions || []);
    } catch (e: any) {
      console.error(e);
    }
  }

  // Real multipart upload function
  async function handleUpload() {
    if (!files || files.length === 0) {
      setLog("No files selected.");
      return;
    }

    setLoading(true);
    setLog("");

    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    try {
      const res = await fetch(`${API}/admin/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Upload failed: ${res.status} ${text}`);
      }

      const body = await res.json();
      setLog(JSON.stringify(body, null, 2));
      setFiles(null);
      fetchVersions();
    } catch (e: any) {
      setLog(e.message || "Upload error");
    } finally {
      setLoading(false);
    }
  }

  // Demo: ingest a local file path already available on the dev machine
  async function handleUploadLocal() {
    setLoading(true);
    setLog("");
    try {
      // Developer-provided demo file (project docs) — kept only for testing/demo.
      const demoPath = "/mnt/data/[SRS]Software_Requirements_Specification.docx";
      const res = await fetch(`${API}/admin/upload_local`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ local_path: demoPath, name: "SRS-demo" }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Local upload failed: ${res.status} ${text}`);
      }
      const body = await res.json();
      setLog(JSON.stringify(body, null, 2));
      fetchVersions();
    } catch (e: any) {
      setLog(e.message || "Local upload error");
    } finally {
      setLoading(false);
    }
  }

  async function handleProcess(versionId: string) {
    setLoading(true);
    try {
      const res = await fetch(`${API}/admin/process/${versionId}`, { method: "POST" });
      const body = await res.json();
      setLog(JSON.stringify(body, null, 2));
      fetchVersions();
    } catch (e: any) {
      setLog(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleEmbed(versionId: string) {
    setLoading(true);
    try {
      const res = await fetch(`${API}/admin/embed/${versionId}`, { method: "POST" });
      const body = await res.json();
      setLog(JSON.stringify(body, null, 2));
      fetchVersions();
    } catch (e: any) {
      setLog(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleActivate(versionId: string) {
    setLoading(true);
    try {
      const res = await fetch(`${API}/admin/activate/${versionId}`, { method: "POST" });
      const body = await res.json();
      setLog(JSON.stringify(body, null, 2));
      fetchVersions();
    } catch (e: any) {
      setLog(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: string) {
  setLoading(true);
  setLog("");
  try {
    const res = await fetch(`${API}/admin/version/${id}`, {
      method: "DELETE",
    });
    const body = await res.json();
    setLog(JSON.stringify(body, null, 2));
    fetchVersions();
  } catch (e: any) {
    setLog(e.message);
  } finally {
    setLoading(false);
  }
}



  return (
    <div className="min-h-screen bg-neutral-900 text-white p-8">
      <div className="max-w-6xl mx-auto">
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">JurisGPT • Admin Dashboard</h1>
            <p className="text-slate-300 mt-1">Vercel-style admin — upload, process, embed, and activate versions of legal corpora.</p>
          </div>
          <div className="text-sm text-slate-400">Mode: <span className="font-mono">Admin</span></div>
        </header>

        <section className="grid grid-cols-3 gap-6">
          <div className="col-span-2 bg-neutral-800 rounded-lg p-6 shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Upload / Demo</h2>

            <div className="flex gap-3 mb-4 items-center">
              <input
                type="file"
                multiple
                onChange={(e) => setFiles(Array.from(e.target.files || []))}
                className="text-sm text-black rounded px-2 py-1"
              />

              <button
                onClick={handleUpload}
                className="bg-sky-500 text-black px-4 py-2 rounded disabled:opacity-60"
                disabled={loading}
              >
                Upload Files
              </button>

              <button
                onClick={handleUploadLocal}
                className="bg-sky-600 px-4 py-2 rounded"
                disabled={loading}
              >
                Use Demo Local File
              </button>
            </div>

            <div className="mb-4">
              <h3 className="font-medium">Action Log</h3>
              <pre className="mt-2 bg-neutral-900 p-3 rounded text-sm max-h-40 overflow-auto">{log || "No actions yet."}</pre>
            </div>

            <div>
              <h3 className="font-medium mb-2">Versions</h3>
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-slate-300">
                    <th>Name</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {versions.map((v) => (
                    <tr key={v.id} className="border-t border-neutral-700">
                      <td className="py-2">{v.name}</td>
                      <td className="py-2">{v.status}</td>
                      <td className="py-2">{new Date(v.created_at).toLocaleString()}</td>
                      <td className="py-2 flex gap-2">
                        <button onClick={() => handleProcess(v.id)} className="px-2 py-1 bg-amber-500 rounded text-black">Process</button>
                        <button onClick={() => handleEmbed(v.id)} className="px-2 py-1 bg-emerald-500 rounded text-black">Embed</button>
                        <button onClick={() => handleActivate(v.id)} className="px-2 py-1 bg-slate-300 text-black rounded">Activate</button>
                        <button onClick={() => handleDelete(v.id)} className="px-2 py-1 bg-red-500 text-black rounded">Delete</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <aside className="bg-neutral-800 rounded-lg p-6 shadow-lg">
            <h3 className="text-lg font-semibold mb-2">Quick Tools</h3>
            <div className="flex flex-col gap-3">
              <button className="py-2 bg-neutral-700 rounded">View Active Version</button>
              <button className="py-2 bg-neutral-700 rounded">Download Index</button>
              <button
                    onClick={async () => {
                      setLog("");
                      setLoading(true);
                      try {
                        const res = await fetch(`${API}/admin/clear_uploads`, { method: "POST" });
                        const body = await res.json();
                        setLog(JSON.stringify(body, null, 2));
                        fetchVersions();
                      } catch (e: any) {
                        setLog(e.message);
                      } finally {
                        setLoading(false);
                      }
                    }}
                    className="py-2 bg-neutral-700 rounded">
                    Clear Uploads
                  </button>

            </div>
          </aside>
        </section>

        <footer className="mt-8 text-sm text-slate-400">Note: Demo upload uses local path '/mnt/data/[SRS]Software_Requirements_Specification.docx'. Real uploads will save under backend/data/uploads/</footer>
      </div>
    </div>
  );
}
