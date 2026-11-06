import { ImageResponse } from "next/og";

export const alt = "Koach — tu coach de hábitos saludables por WhatsApp";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 24,
          background: "#fafafa",
          color: "#1e293b",
        }}
      >
        <div style={{ fontSize: 140, fontWeight: 700, color: "#10b981" }}>Koach</div>
        <div style={{ fontSize: 48 }}>Tu coach de hábitos saludables en WhatsApp</div>
      </div>
    ),
    { ...size },
  );
}
