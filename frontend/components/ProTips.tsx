import { Lightbulb } from "lucide-react";

export default function ProTips() {
  return (
    <div
      className="
        w-full
        rounded-2xl
        border border-violet-500/20
        bg-gradient-to-br from-gray-900 via-gray-900 to-black
        p-5
        shadow-lg
      "
    >
      {/* Header */}
      <div className="flex items-center space-x-3 mb-4">
        <div className="w-9 h-9 rounded-full bg-violet-500/20 flex items-center justify-center">
          <Lightbulb className="w-5 h-5 text-violet-400" />
        </div>
        <h3 className="text-base font-semibold text-violet-300">
          Pro Tips for Better Results
        </h3>
      </div>

      {/* Tips */}
      <ul className="space-y-3 text-sm text-gray-300">
        <li className="flex items-start space-x-2">
          <span className="text-lime-400 mt-1">•</span>
          <span>
            <span className="text-white font-medium">Be specific:</span>{" "}
            Include movie titles, actor names, or time periods
          </span>
        </li>

        <li className="flex items-start space-x-2">
          <span className="text-lime-400 mt-1">•</span>
          <span>
            Ask <span className="text-white font-medium">one question at a time</span>{" "}
            for more accurate answers
          </span>
        </li>

        <li className="flex items-start space-x-2">
          <span className="text-lime-400 mt-1">•</span>
          <span className="flex items-center space-x-2">
            <span>Press</span>
            <kbd className="px-2 py-0.5 rounded-md bg-gray-800 border border-gray-700 text-xs text-violet-300">
              Shift
            </kbd>
            <span>+</span>
            <kbd className="px-2 py-0.5 rounded-md bg-gray-800 border border-gray-700 text-xs text-violet-300">
              Enter
            </kbd>
            <span>for new lines</span>
          </span>
        </li>
      </ul>
    </div>
  );
}
