import { useState } from "react"
import { analyzeInstagram } from "../services/api"

export default function Instagram() {
  const [api_key, setApiKey] = useState("")     // ✅ FIX
  const [username, setUsername] = useState("")
  const [date_filter, setDateFilter] = useState("")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    if (!api_key || !username) {
      setError("API Key and Username are required")
      return
    }

    setLoading(true)
    setError(null)

    try {
      const res = await analyzeInstagram({
        api_key,
        username,
        date_filter
      })
      setResult(res)
    } catch (err) {
      setError(err.response?.data?.detail || "Analysis failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gray-800 p-6 rounded-xl shadow-lg space-y-4">
      <h2 className="text-2xl font-bold">📸 Instagram Analyzer</h2>

      {/* API KEY */}
      <input
        className="w-full p-2 rounded text-black"
        placeholder="Enter Apify API Key"
        value={api_key}
        onChange={(e) => setApiKey(e.target.value)}
      />

      {/* USERNAME */}
      <input
        className="w-full p-2 rounded text-black"
        placeholder="Instagram Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />

      {/* DATE FILTER */}
      <input
        className="w-full p-2 rounded text-black"
        placeholder="Date filter (e.g. 7 days)"
        value={date_filter}
        onChange={(e) => setDateFilter(e.target.value)}
      />

      <button
        onClick={handleAnalyze}
        className="w-full bg-pink-600 hover:bg-pink-700 p-2 rounded"
      >
        {loading ? "Analyzing..." : "Analyze"}
      </button>

      {error && <p className="text-red-400">{error}</p>}

      {result && (
        <pre className="bg-black p-3 rounded text-sm overflow-auto">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  )
}
