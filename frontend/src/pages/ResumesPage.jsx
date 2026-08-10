import React, { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import Layout from "../components/Layout.jsx";
import { Card, PrimaryButton, SecondaryButton, Spinner, ErrorBanner } from "../components/ui.jsx";
import { resumesApi } from "../api/endpoints.js";

export default function ResumesPage() {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setResumes(await resumesApi.list());
    } catch {
      setError("Could not load your resumes");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      await resumesApi.upload(file);
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not upload the file");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleNewVersion = async (parentId, e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      await resumesApi.upload(file, null, parentId);
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not upload the new version");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this resume and all related analyses?")) return;
    await resumesApi.remove(id);
    await load();
  };

  const handleViewFile = async (id) => {
    try {
      const blob = await resumesApi.fileBlob(id);
      const url = window.URL.createObjectURL(blob);
      window.open(url, "_blank", "noopener,noreferrer");
      setTimeout(() => window.URL.revokeObjectURL(url), 30000);
    } catch {
      setError("Could not open the resume file");
    }
  };

  return (
    <Layout>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display text-2xl font-semibold">Resumes</h1>
          <p className="text-text-muted text-sm mt-1">Upload a resume to start analyzing it against a job</p>
        </div>
        <label>
          <input type="file" accept=".pdf,.docx" className="hidden" onChange={handleUpload} disabled={uploading} />
          <PrimaryButton as="span" className="cursor-pointer">
            {uploading ? "Uploading..." : "+ Upload resume"}
          </PrimaryButton>
        </label>
      </div>

      <ErrorBanner message={error} />

      {loading ? (
        <Spinner label="Loading resumes..." />
      ) : resumes.length === 0 ? (
        <Card className="text-center py-12">
          <p className="text-text-muted text-sm">No resumes yet. Upload a PDF or DOCX to get started.</p>
        </Card>
      ) : (
        <div className="grid gap-3">
          {resumes.map((resume) => (
            <Card key={resume.id} className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{resume.parsed_data?.name || resume.original_filename}</div>
                <div className="text-xs text-text-muted font-mono mt-1">
                  {resume.label} · {resume.file_type.toUpperCase()} · {resume.parsed_data?.skills?.length || 0} skills
                </div>
                <div className="text-xs text-text-faint mt-1">
                  Added{" "}
                  {new Date(resume.created_at).toLocaleDateString("en-US", {
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                  })}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleViewFile(resume.id)}
                  className="text-sm text-text-muted hover:text-signal px-2"
                  title="View file"
                >
                  File
                </button>
                <Link to={`/resumes/${resume.id}/versions`}>
                  <SecondaryButton>Versions</SecondaryButton>
                </Link>
                <Link to={`/analyze?resumeId=${resume.id}`}>
                  <PrimaryButton>Analyze</PrimaryButton>
                </Link>
                <label>
                  <input
                    type="file"
                    accept=".pdf,.docx"
                    className="hidden"
                    onChange={(e) => handleNewVersion(resume.id, e)}
                  />
                  <SecondaryButton as="span" className="cursor-pointer" title="Upload a new version">
                    + Version
                  </SecondaryButton>
                </label>
                <button
                  onClick={() => handleDelete(resume.id)}
                  className="text-text-faint hover:text-gap text-sm px-2"
                  title="Delete"
                >
                  ✕
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </Layout>
  );
}
