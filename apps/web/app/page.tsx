"use client"

import React, { useState, useEffect, useCallback } from 'react'
import { Sparkles, Zap } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { UploadZone } from '@/components/upload-zone'
import { StyleSelector } from '@/components/style-selector'
import { ProgressIndicator } from '@/components/progress-indicator'
import { ResultViewer } from '@/components/result-viewer'
import { api } from '@/lib/api'
import { JobResponse, StylePreset, JobStatus } from '@/lib/types'

type AppState = 'upload' | 'processing' | 'result' | 'error'

export default function Home() {
  // State
  const [appState, setAppState] = useState<AppState>('upload')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [selectedStyle, setSelectedStyle] = useState<string | null>(null)
  const [styles, setStyles] = useState<StylePreset[]>([])
  const [currentJob, setCurrentJob] = useState<JobResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // Load styles on mount
  useEffect(() => {
    async function loadStyles() {
      try {
        const response = await api.getStyles()
        setStyles(response.styles)
      } catch (err) {
        console.error('Failed to load styles:', err)
        // Use fallback styles for demo
        setStyles([
          { id: 'classic-tuxedo', name: 'Classic Tuxedo', description: 'Elegant spy archetype in formal evening wear', prompt: '', thumbnail: null },
          { id: 'streetwear', name: 'Modern Streetwear', description: 'Urban fashion with hoodies and sneakers', prompt: '', thumbnail: null },
          { id: 'techwear', name: 'Techwear', description: 'Functional futuristic clothing', prompt: '', thumbnail: null },
          { id: 'old-money', name: 'Old Money', description: 'Refined preppy aesthetic', prompt: '', thumbnail: null },
          { id: 'minimalist', name: 'Minimalist', description: 'Clean, simple, monochrome looks', prompt: '', thumbnail: null },
          { id: 'cyberpunk', name: 'Cyberpunk', description: 'Neon-accented futuristic fashion', prompt: '', thumbnail: null },
          { id: 'crypto-bro', name: 'Crypto Bro', description: 'Tech founder vibes with hoodies and Patagonia vests', prompt: '', thumbnail: null },
        ])
      }
    }
    loadStyles()
  }, [])

  // Handle file selection
  const handleFileSelect = useCallback((file: File) => {
    setSelectedFile(file)
    setPreviewUrl(URL.createObjectURL(file))
    setError(null)
  }, [])

  // Handle file clear
  const handleClearFile = useCallback(() => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }
    setSelectedFile(null)
    setPreviewUrl(null)
    setSelectedStyle(null)
    setError(null)
  }, [previewUrl])

  // Handle generation
  const handleGenerate = async () => {
    if (!selectedFile || !selectedStyle) return

    setIsLoading(true)
    setError(null)
    setAppState('processing')

    try {
      // Create job
      const job = await api.createJob(selectedFile, selectedStyle)
      setCurrentJob(job)

      // Poll for completion
      const finalJob = await api.pollJob(
        job.job_id,
        (updatedJob) => setCurrentJob(updatedJob),
        1000,
        300000
      )

      if (finalJob.status === 'completed' && finalJob.result_url) {
        setCurrentJob(finalJob)
        setAppState('result')
      } else if (finalJob.status === 'failed') {
        setError(finalJob.error || 'Generation failed')
        setAppState('error')
      }
    } catch (err) {
      console.error('Generation failed:', err)
      setError(err instanceof Error ? err.message : 'Generation failed')
      setAppState('error')
    } finally {
      setIsLoading(false)
    }
  }

  // Handle reset
  const handleReset = useCallback(() => {
    handleClearFile()
    setCurrentJob(null)
    setAppState('upload')
    setError(null)
  }, [handleClearFile])

  // Get selected style name
  const selectedStyleName = styles.find(s => s.id === selectedStyle)?.name || ''

  // Can generate?
  const canGenerate = selectedFile && selectedStyle && !isLoading

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold gradient-text">StyleForge</h1>
                <p className="text-xs text-muted-foreground">AI Style Transfer</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12">
        {/* Hero */}
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Transform Your <span className="gradient-text">Style</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Upload a photo and instantly see yourself in different fashion styles.
            Your face stays the same, only the outfit changes.
          </p>
        </div>

        {/* Upload State */}
        {appState === 'upload' && (
          <div className="max-w-4xl mx-auto space-y-12">
            {/* Step 1: Upload */}
            <section>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold text-sm">
                  1
                </div>
                <h3 className="text-xl font-semibold">Upload Your Photo</h3>
              </div>
              <div className="max-w-md mx-auto">
                <UploadZone
                  onFileSelect={handleFileSelect}
                  selectedFile={selectedFile}
                  onClear={handleClearFile}
                  disabled={isLoading}
                />
              </div>
            </section>

            {/* Step 2: Choose Style */}
            {selectedFile && (
              <section className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold text-sm">
                    2
                  </div>
                  <h3 className="text-xl font-semibold">Choose a Style</h3>
                </div>
                <StyleSelector
                  styles={styles}
                  selectedStyle={selectedStyle}
                  onSelect={setSelectedStyle}
                  disabled={isLoading}
                />
              </section>
            )}

            {/* Generate Button */}
            {selectedFile && selectedStyle && (
              <div className="flex justify-center animate-in fade-in slide-in-from-bottom-4 duration-500">
                <Button
                  size="xl"
                  onClick={handleGenerate}
                  disabled={!canGenerate}
                  className="gap-2"
                >
                  <Zap className="h-5 w-5" />
                  Generate New Look
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Processing State */}
        {appState === 'processing' && currentJob && (
          <div className="max-w-md mx-auto py-12">
            <ProgressIndicator
              status={currentJob.status}
              progress={currentJob.progress}
              error={currentJob.error}
            />
          </div>
        )}

        {/* Result State */}
        {appState === 'result' && currentJob?.result_url && previewUrl && (
          <div className="max-w-4xl mx-auto">
            <ResultViewer
              originalUrl={previewUrl}
              resultUrl={api.getResultUrl(currentJob.result_url)}
              styleName={selectedStyleName}
              onReset={handleReset}
            />
          </div>
        )}

        {/* Error State */}
        {appState === 'error' && (
          <div className="max-w-md mx-auto text-center py-12">
            <ProgressIndicator
              status="failed"
              progress={0}
              error={error}
            />
            <Button
              variant="outline"
              onClick={handleReset}
              className="mt-6"
            >
              Try Again
            </Button>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-border mt-auto">
        <div className="container mx-auto px-4 py-6">
          <p className="text-center text-sm text-muted-foreground">
            StyleForge • AI-powered style transfer • Your identity, new style
          </p>
        </div>
      </footer>
    </div>
  )
}

