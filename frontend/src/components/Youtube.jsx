import { useState } from "react"
import { analyzeYouTube } from "../services/api"

export default function Youtube() {
  const [apiKey, setApiKey] = useState("")
  const [handle, setHandle] = useState("")
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleAnalyze = async () => {
    setError("")
    setData(null)

    if (!apiKey || !handle) {
      setError("API key and channel handle are required")
      return
    }

    try {
      setLoading(true)

      const res = await analyzeYouTube({
        api_key: apiKey,
        handle
      })

      setData(res)
    } catch (err) {
      console.error(err)
      setError(
        err?.response?.data?.detail ||
        "Failed to analyze YouTube channel"
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gray-800 p-6 rounded-xl shadow-lg space-y-4">
      <h2 className="text-2xl font-bold text-red-500">
        ▶️ YouTube Competitor Analyzer
      </h2>

      {/* API KEY */}
      <input
        className="w-full p-2 rounded text-black"
        placeholder="Enter your YouTube Data API v3 Key"
        value={apiKey}
        onChange={(e) => setApiKey(e.target.value)}
      />

      {/* CHANNEL HANDLE */}
      <input
        className="w-full p-2 rounded text-black"
        placeholder="Enter channel handle (e.g. @fazerug)"
        value={handle}
        onChange={(e) => setHandle(e.target.value)}
      />

      {/* BUTTON */}
      <button
        onClick={handleAnalyze}
        className="w-full bg-red-600 hover:bg-red-700 p-2 rounded text-white font-semibold"
      >
        {loading ? "Analyzing..." : "Analyze Channel"}
      </button>

      {/* ERROR */}
      {error && (
        <p className="text-red-400 text-sm">{error}</p>
      )}

      {/* RESULT */}
      {data && (
        <div className="mt-4 bg-gray-900 p-4 rounded-lg space-y-2 text-sm">
          <p><b>Channel:</b> {data.channel.name}</p>
          <p><b>Subscribers:</b> {data.channel.subscribers.toLocaleString()}</p>
          <p><b>Avg Views:</b> {data.channel.avg_views.toLocaleString()}</p>
          <p><b>Avg Likes:</b> {data.channel.avg_likes.toLocaleString()}</p>
          <p><b>Engagement:</b> {data.channel.engagement}%</p>

          <hr className="border-gray-700 my-2" />

          <p className="font-semibold text-yellow-400">
            Competitors (Average)
          </p>
          <p>Avg Views: {Math.round(data.competitors_avg.avg_views).toLocaleString()}</p>
          <p>Avg Likes: {Math.round(data.competitors_avg.avg_likes).toLocaleString()}</p>
          <p>Engagement: {data.competitors_avg.engagement.toFixed(2)}%</p>
        </div>
      )}
    </div>
  )
}
