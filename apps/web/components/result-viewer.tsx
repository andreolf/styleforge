"use client"

import React, { useState } from 'react'
import { Download, RotateCcw, SplitSquareHorizontal, Image as ImageIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { BeforeAfterSlider } from '@/components/before-after-slider'
import { cn } from '@/lib/utils'

interface ResultViewerProps {
  originalUrl: string
  resultUrl: string
  styleName: string
  onReset: () => void
}

type ViewMode = 'compare' | 'result' | 'original'

export function ResultViewer({ originalUrl, resultUrl, styleName, onReset }: ResultViewerProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('compare')

  const handleDownload = async () => {
    try {
      const response = await fetch(resultUrl)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `styleforge-${styleName.toLowerCase().replace(/\s+/g, '-')}.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  return (
    <div className="space-y-6">
      {/* View mode tabs */}
      <div className="flex items-center justify-center gap-2">
        <Button
          variant={viewMode === 'compare' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setViewMode('compare')}
        >
          <SplitSquareHorizontal className="h-4 w-4 mr-2" />
          Compare
        </Button>
        <Button
          variant={viewMode === 'result' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setViewMode('result')}
        >
          <ImageIcon className="h-4 w-4 mr-2" />
          Result
        </Button>
        <Button
          variant={viewMode === 'original' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setViewMode('original')}
        >
          Original
        </Button>
      </div>

      {/* Image display */}
      <div className="relative max-w-2xl mx-auto">
        {viewMode === 'compare' ? (
          <BeforeAfterSlider
            beforeSrc={originalUrl}
            afterSrc={resultUrl}
            beforeLabel="Original"
            afterLabel={styleName}
          />
        ) : (
          <div className="aspect-square rounded-lg overflow-hidden bg-card">
            <img
              src={viewMode === 'result' ? resultUrl : originalUrl}
              alt={viewMode === 'result' ? styleName : 'Original'}
              className="w-full h-full object-cover"
            />
          </div>
        )}
      </div>

      {/* Action buttons */}
      <div className="flex items-center justify-center gap-4">
        <Button
          variant="outline"
          onClick={onReset}
        >
          <RotateCcw className="h-4 w-4 mr-2" />
          Try Another
        </Button>
        <Button
          onClick={handleDownload}
        >
          <Download className="h-4 w-4 mr-2" />
          Download Result
        </Button>
      </div>

      {/* Style info */}
      <p className="text-center text-sm text-muted-foreground">
        Style applied: <span className="font-medium text-foreground">{styleName}</span>
      </p>
    </div>
  )
}

