import React, { ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    console.error("ErrorBoundary.getDerivedStateFromError:", error);
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("ErrorBoundary.componentDidCatch:", error, errorInfo);
    // Log to console so user can see it in DevTools
    console.error("Stack:", errorInfo.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            display: "block",
            width: "100%",
            height: "100vh",
            backgroundColor: "#f8f9fa",
            padding: "40px 20px",
            fontFamily: "monospace",
            overflowY: "auto",
          }}
        >
          <div style={{ maxWidth: "800px", margin: "0 auto" }}>
            <h1 style={{ color: "#d32f2f", marginBottom: "20px", fontSize: "24px" }}>
              🚨 React Error - App Crashed
            </h1>
            <h2 style={{ color: "#666", fontSize: "16px", marginBottom: "10px" }}>
              Error Message:
            </h2>
            <pre
              style={{
                backgroundColor: "#fff3cd",
                border: "1px solid #ffc107",
                padding: "15px",
                borderRadius: "4px",
                overflow: "auto",
                marginBottom: "20px",
                fontSize: "12px",
              }}
            >
              {this.state.error?.message || "Unknown error"}
            </pre>

            <h2 style={{ color: "#666", fontSize: "16px", marginBottom: "10px" }}>
              Stack Trace:
            </h2>
            <pre
              style={{
                backgroundColor: "#ffebee",
                border: "1px solid #f44336",
                padding: "15px",
                borderRadius: "4px",
                overflow: "auto",
                marginBottom: "20px",
                fontSize: "11px",
                lineHeight: "1.4",
                color: "#d32f2f",
              }}
            >
              {this.state.error?.stack || "No stack trace available"}
            </pre>

            <button
              onClick={() => {
                console.log("Reloading page...");
                window.location.reload();
              }}
              style={{
                padding: "12px 24px",
                backgroundColor: "#007bff",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: "bold",
              }}
            >
              Reload Page
            </button>

            <div style={{ marginTop: "30px", padding: "15px", backgroundColor: "#e3f2fd", borderRadius: "4px" }}>
              <strong>Debug Info:</strong>
              <p>Check your browser console (F12 → Console tab) for more details.</p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

