export type UploadResponse = {
  video_id: string;
  filename: string;
  status: string;
};

export type StatusResponse = {
  video_id: string;
  status: string;
  filename: string;
  error: string | null;
  progress: number;
};

export type AnalysisEvent = {
  id: string;
  event_type: string;
  timestamp_seconds: number;
  track_id: number;
  object_class: string;
  confidence: number;
  metadata: Record<string, string | number>;
};

export type AnalysisResult = {
  video_id: string;
  status: string;
  frame_count: number;
  processing_seconds: number;
  average_fps: number;
  output_url: string;
  events: AnalysisEvent[];
  analytics: {
    entries?: number;
    exits?: number;
    occupancy?: number;
    active_tracks?: number;
  };
};

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const detail = payload?.detail ?? `Request failed with status ${response.status}`;
    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}

export async function uploadVideo(file: File): Promise<UploadResponse> {
  const body = new FormData();
  body.append("file", file);

  const response = await fetch("/api/videos", {
    method: "POST",
    body,
  });

  return parseJson<UploadResponse>(response);
}

export async function startAnalysis(videoId: string): Promise<void> {
  const response = await fetch(`/api/videos/${videoId}/analyze`, {
    method: "POST",
  });

  await parseJson<Record<string, string>>(response);
}

export async function getStatus(videoId: string): Promise<StatusResponse> {
  const response = await fetch(`/api/videos/${videoId}`);
  return parseJson<StatusResponse>(response);
}

export async function getResult(videoId: string): Promise<AnalysisResult> {
  const response = await fetch(`/api/videos/${videoId}/result`);
  return parseJson<AnalysisResult>(response);
}
