import Instagram from "../components/Instagram"
import YouTube from "../components/Youtube"

export default function Home() {
  return (
    <div className="max-w-5xl mx-auto p-6">
      <h1 className="text-4xl font-bold text-center mb-10">
        📊 Social Media Scraper
      </h1>

      <div className="grid md:grid-cols-2 gap-6">
        <Instagram />
        <YouTube />
      </div>
    </div>
  )
}
