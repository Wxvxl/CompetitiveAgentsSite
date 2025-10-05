"use client";

import { useState } from "react";
import ContestCreationForm from "@/components/contests/ContestCreationForm";
import ContestList from "@/components/contests/ContestList";
import ContestDetailsView from "@/components/contests/ContestDetailsView";
import Modal from "@/components/ui/Modal";

export default function ContestsPage() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedContestId, setSelectedContestId] = useState<number | null>(
    null
  );

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold">Contest Management</h1>
            <p className="text-gray-600 mt-1">
              Create and manage mini-contests between agents (FR3.1-FR3.4)
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600 transition"
          >
            Create Contest
          </button>
        </div>

        {/* Contest List */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">All Contests</h2>
          <ContestList onViewDetails={(id) => setSelectedContestId(id)} />
        </div>

        {/* Create Contest Modal */}
        <Modal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          title="Create New Contest"
        >
          <ContestCreationForm
            onSuccess={() => {
              setShowCreateModal(false);
            }}
          />
        </Modal>

        {/* Contest Details Modal */}
        <Modal
          isOpen={selectedContestId !== null}
          onClose={() => setSelectedContestId(null)}
          title="Contest Details"
        >
          {selectedContestId !== null && (
            <ContestDetailsView
              contestId={selectedContestId}
              onClose={() => setSelectedContestId(null)}
            />
          )}
        </Modal>
      </div>
    </div>
  );
}
