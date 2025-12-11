import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Suspense, lazy } from "react";

console.log("AppContent imports loaded successfully");

// Candidate Pages - Lazy loaded
const CandidateLogin = lazy(() => import("@/pages/CandidateLogin"));
const CandidateTests = lazy(() => import("@/pages/candidate/CandidateTests"));
const CandidateCompleted = lazy(() => import("@/pages/candidate/CandidateCompleted"));
const TestInstructions = lazy(() => import("@/pages/candidate/TestInstructions"));
const TestTaking = lazy(() => import("@/pages/candidate/TestTaking"));
const TestSubmitted = lazy(() => import("@/pages/candidate/TestSubmitted"));

import NotFound from "@/pages/NotFound";

const queryClient = new QueryClient();

console.log("AppContent component defining...");

const LoadingFallback = () => (
  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh", fontFamily: "sans-serif" }}>
    <div>Loading...</div>
  </div>
);

export default function AppContent() {
  console.log("AppContent rendering");
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Suspense fallback={<LoadingFallback />}>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Navigate to="/candidate/login" replace />} />
              <Route path="/candidate/login" element={<CandidateLogin />} />

              {/* Candidate Routes */}
              <Route path="/candidate/tests" element={<CandidateTests />} />
              <Route path="/candidate/completed" element={<CandidateCompleted />} />
              <Route path="/candidate/test/:assignmentId/start" element={<TestInstructions />} />
              <Route path="/candidate/test/:assignmentId/submitted" element={<TestSubmitted />} />
              <Route path="/candidate/test/:assignmentId" element={<TestTaking />} />

              {/* Catch All */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
}
