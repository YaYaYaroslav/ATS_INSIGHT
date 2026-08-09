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
      const data = await resumesApi.list();
      setResumes(data);
    } catch (err) {
      setError("Не вдалося завантажити список резюме");
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
      setError(err.response?.data?.detail || "Не вдалося завантажити файл");
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
      setError(err.response?.data?.detail || "Не вдалося завантажити нову версію");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Видалити це резюме та всі пов'язані аналізи?")) return;
    await resumesApi.remove(id);
    await load();
  };

  const handleViewFile = async (id) => {
    try {
      const blob = await resumesApi.fileBlob(id);
      const url = window.URL.createObjectURL(blob);
      window.open(url, "_blank", "noopener,noreferrer");
      // Звільняємо об'єктний URL трохи згодом, давши вкладці час відкритись
      setTimeout(() => window.URL.revokeObjectURL(url), 30000);
    } catch (err) {
      setError("Не вдалося відкрити файл резюме");
    }
  };

  return (
    <Layout>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display text-2xl font-semibold">Резюме</h1>
          <p className="text-text-muted text-sm mt-1">Завантаж резюме, щоб почати аналіз проти вакансії</p>
        </div>
        <label>
          <input type="file" accept=".pdf,.docx" className="hidden" onChange={handleUpload} disabled={uploading} />
          <PrimaryButton as="span" className="cursor-pointer">
            {uploading ? "Завантаження..." : "+ Завантажити резюме"}
          </PrimaryButton>
        </label>
      </div>

      <ErrorBanner message={error} />

      {loading ? (
        <Spinner label="Завантажую резюме..." />
      ) : resumes.length === 0 ? (
        <Card className="text-center py-12">
          <p className="text-text-muted text-sm">
            Ще немає жодного резюме. Завантаж PDF або DOCX, щоб почати.
          </p>
        </Card>
      ) : (
        <div className="grid gap-3">
          {resumes.map((resume) => (
            <Card key={resume.id} className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">
                  {resume.parsed_data?.name || resume.original_filename}
                </div>
                <div className="text-xs text-text-muted font-mono mt-1">
                  {resume.label} · {resume.file_type.toUpperCase()} · {resume.parsed_data?.skills?.length || 0} навичок
                </div>
                <div className="text-xs text-text-faint mt-1">
                  Додано {new Date(resume.created_at).toLocaleDateString("uk-UA", { day: "numeric", month: "short", year: "numeric" })}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleViewFile(resume.id)}
                  className="text-sm text-text-muted hover:text-signal px-2"
                  title="Переглянути файл"
                >
                  Файл
                </button>
                <Link to={`/resumes/${resume.id}/versions`}>
                  <SecondaryButton>Версії</SecondaryButton>
                </Link>
                <Link to={`/analyze?resumeId=${resume.id}`}>
                  <PrimaryButton>Аналізувати</PrimaryButton>
                </Link>
                <label>
                  <input
                    type="file"
                    accept=".pdf,.docx"
                    className="hidden"
                    onChange={(e) => handleNewVersion(resume.id, e)}
                  />
                  <SecondaryButton as="span" className="cursor-pointer" title="Завантажити нову версію">
                    + Версія
                  </SecondaryButton>
                </label>
                <button
                  onClick={() => handleDelete(resume.id)}
                  className="text-text-faint hover:text-gap text-sm px-2"
                  title="Видалити"
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
