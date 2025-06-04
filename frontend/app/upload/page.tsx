"use client";
import { useState } from "react";
import DataSetSelectionModal, {
  type DataSet, // ← note  type  keyword
} from "@/components/DataSetSelectionModal";

export default function UploadPage() {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<DataSet | null>(null);

  return (
    <>
      <button onClick={() => setOpen(true)} className="btn">
        Upload EEG CSV
      </button>

      <DataSetSelectionModal
        isOpen={open}
        onClose={() => {
          setOpen(false);
          setSelected(null);
        }}
        selectedDataSet={selected}
        onSelectDataSet={setSelected}
      />
    </>
  );
}
