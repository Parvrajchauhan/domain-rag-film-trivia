"use client";

import { useEffect, useState } from "react";
import { Info, X, Film } from "lucide-react";

interface Movie {
  doc_id: string;
  title: string;
  source: string;
}

export default function InfoPanel() {
  const [open, setOpen] = useState(false);
  const [movies, setMovies] = useState<Movie[]>([]);

  useEffect(() => {
    if (!open) return;

    const loadCSV = async () => {
      const res = await fetch("/data/catalog.csv");
      const text = await res.text();

      const lines = text.trim().split("\n");
      const [, ...rows] = lines;

      const parsed: Movie[] = rows.map((row) => {
        const [doc_id, title, source] = row.split(",");
        return { doc_id, title, source };
      });

      setMovies(parsed);
    };

    loadCSV();
  }, [open]);

  return (
    <>
      {/* INFO ICON (top-right) */}
      <button
        onClick={() => setOpen(true)}
        className="
          fixed top-6 right-6 z-50
          w-10 h-10 rounded-full
          bg-gradient-to-br from-gray-800 to-gray-900
          border border-gray-700
          flex items-center justify-center
          hover:border-violet-500
          transition
        "
      >
        <Info className="w-5 h-5 text-violet-400" />
      </button>

      {/* MODAL */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setOpen(false)}
          />

          {/* Panel */}
          <div
            className="
              relative w-full max-w-lg mx-4
              bg-gradient-to-br from-gray-900 to-black
              border border-gray-800
              rounded-2xl
              shadow-2xl
            "
          >
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-gray-800">
              <h3 className="text-lg font-semibold text-violet-300 flex items-center gap-2">
                <Film className="w-5 h-5" />
                Supported Movies
              </h3>

              <button
                onClick={() => setOpen(false)}
                className="text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* List */}
            <div className="max-h-[60vh] overflow-y-auto p-4 space-y-2 custom-scrollbar">
              {movies.map((movie) => (
                <div
                  key={movie.doc_id}
                  className="
                    px-4 py-3 rounded-xl
                    bg-gradient-to-br from-gray-800 to-gray-900
                    border border-gray-700
                    hover:border-lime-400
                    transition
                  "
                >
                  <p className="text-sm text-white font-medium">
                    {movie.title}
                  </p>
                  <p className="text-xs text-gray-400">
                    Source: {movie.source}
                  </p>
                </div>
              ))}

              {movies.length === 0 && (
                <p className="text-sm text-gray-400">
                  Loading movies…
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
