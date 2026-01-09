import axios from "axios"

// 🔹 Base backend URL
const BASE_URL = "http://localhost:8000"

/* ================================
   INSTAGRAM ANALYSIS
================================ */

export const analyzeInstagram = async ({
  api_key,
  username,
  date_filter = null
}) => {
  const response = await axios.post(
    `${BASE_URL}/instagram/analyze`,
    {
      api_key,
      username,
      date_filter
    }
  )

  return response.data
}

/* ================================
   YOUTUBE ANALYSIS
================================ */

export const analyzeYouTube = async ({
  api_key,
  handle
}) => {
  const response = await axios.post(
    `${BASE_URL}/youtube/analyze`,
    {
      api_key,
      handle
    }
  )

  return response.data
}
