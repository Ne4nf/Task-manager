import { useState } from 'react';
import { GitBranch, Loader2, FileText, CheckCircle2, Sparkles } from 'lucide-react';

interface GitAnalyzerProps {
  projectId: string;
  onAnalyzeComplete?: () => void;
}

export default function GitAnalyzer({ projectId, onAnalyzeComplete }: GitAnalyzerProps) {
  const [gitUrl, setGitUrl] = useState('');
  const [accessToken, setAccessToken] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!gitUrl.trim()) {
      setError('Please enter a Git repository URL');
      return;
    }

    setIsAnalyzing(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/git-analyzer/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': localStorage.getItem('user_id') || '',
        },
        body: JSON.stringify({
          git_url: gitUrl,
          project_id: projectId,
          access_token: accessToken || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const data = await response.json();
      setResult(data);
      
      if (onAnalyzeComplete) {
        onAnalyzeComplete();
      }
    } catch (err: any) {
      console.error('Git analysis error:', err);
      setError(err.message || 'Failed to analyze repository');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-200">
        <div className="flex items-start gap-3 mb-4">
          <div className="w-10 h-10 rounded-lg bg-purple-500 flex items-center justify-center flex-shrink-0">
            <GitBranch className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1">
            <h4 className="font-bold text-gray-800 mb-1">AI-Powered Repository Analysis</h4>
            <p className="text-sm text-gray-600">
              Automatically analyze your Git repository with Repomix + Claude AI to generate comprehensive project documentation
            </p>
          </div>
        </div>

        <div className="space-y-4">
          {/* Git URL Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Git Repository URL *
            </label>
            <input
              type="url"
              value={gitUrl}
              onChange={(e) => setGitUrl(e.target.value)}
              placeholder="https://github.com/username/repository"
              className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              disabled={isAnalyzing}
            />
          </div>

          {/* Access Token Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Access Token (Optional)
              <span className="text-gray-500 text-xs ml-2">For private repositories</span>
            </label>
            <input
              type="password"
              value={accessToken}
              onChange={(e) => setAccessToken(e.target.value)}
              placeholder="ghp_xxxxxxxxxxxxxxxxxxxxx"
              className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              disabled={isAnalyzing}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
              {error}
            </div>
          )}

          {/* Analyze Button */}
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing || !gitUrl.trim()}
            className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 px-6 rounded-xl font-medium hover:shadow-lg transform hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing Repository...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Analyze with AI
              </>
            )}
          </button>
        </div>
      </div>

      {/* Analysis Result */}
      {result && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-6">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
            <div className="flex-1">
              <h4 className="font-bold text-green-800 mb-2">Analysis Complete!</h4>
              <div className="space-y-2 text-sm text-gray-700">
                <p><strong>Repository:</strong> {result.repository_name}</p>
                <p><strong>Status:</strong> <span className="text-green-600">{result.status}</span></p>
                {result.document_id && (
                  <p className="flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    <span>Documentation saved (ID: {result.document_id.slice(0, 8)}...)</span>
                  </p>
                )}
                <p className="text-gray-600 mt-3">
                  The AI has analyzed your repository and generated comprehensive documentation. 
                  You can now use this to generate modules and tasks automatically!
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Info Box */}
      {!result && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <h5 className="font-medium text-blue-900 mb-2 text-sm">How it works:</h5>
          <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
            <li>Repomix bundles your entire codebase into a single file</li>
            <li>Claude AI analyzes the code structure and patterns</li>
            <li>Generates comprehensive documentation following SKILL.md template</li>
            <li>Saves to database for AI module/task generation</li>
          </ol>
        </div>
      )}
    </div>
  );
}
