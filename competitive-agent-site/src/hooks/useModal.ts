import { useState } from "react";

export default function useModal(initial = false) {
  const [open, setOpen] = useState<boolean>(initial);
  return {
    open,
    openModal: () => setOpen(true),
    closeModal: () => setOpen(false),
    toggle: () => setOpen((v) => !v),
    setOpen,
  } as const;
}


