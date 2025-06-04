// components/ui/spinner.tsx
"use client";

export function Spinner() {
  return (
    <div className="flex justify-center">
      <div className="h-8 w-8 border-4 border-blue-300 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}
