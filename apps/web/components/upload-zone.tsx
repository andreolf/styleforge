"use client"

import React, { useCallback, useState } from 'react'
import { Upload, X, Image as ImageIcon } from 'lucide-react'
import { cn, formatFileSize, isValidImageFile } from '@/lib/utils'
import { Button } from '@/components/ui/button'

interface UploadZoneProps {
  onFileSelect: (file: File) => void
  selectedFile: File | null
  onClear: () => void
  disabled?: boolean
}

export function UploadZone({ onFileSelect, selectedFile, onClear, disabled }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFile = useCallback((file: File) => {
    setError(null)
    
    if (!isValidImageFile(file)) {
      setError('Please upload a valid image file (JPG, PNG, or WebP)')
      return
    }
    
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB')
      return
    }
    
    // Create preview URL
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
    onFileSelect(file)
  }, [onFileSelect])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    if (!disabled) {
      setIsDragging(true)
    }
  }, [disabled])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    if (disabled) return
    
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFile(files[0])
    }
  }, [disabled, handleFile])

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFile(files[0])
    }
  }, [handleFile])

  const handleClear = useCallback(() => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }
    setPreviewUrl(null)
    setError(null)
    onClear()
  }, [previewUrl, onClear])

  // Cleanup on unmount
  React.useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl)
      }
    }
  }, [previewUrl])

  if (selectedFile && previewUrl) {
    return (
      <div className="relative rounded-lg border-2 border-border bg-card overflow-hidden">
        <div className="aspect-square relative">
          <img
            src={previewUrl}
            alt="Preview"
            className="w-full h-full object-cover"
          />
          {!disabled && (
            <Button
              variant="destructive"
              size="icon"
              className="absolute top-3 right-3"
              onClick={handleClear}
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
        <div className="p-4 border-t border-border">
          <p className="text-sm font-medium truncate">{selectedFile.name}</p>
          <p className="text-xs text-muted-foreground">{formatFileSize(selectedFile.size)}</p>
        </div>
      </div>
    )
  }

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={cn(
        "drop-zone relative rounded-lg border-2 border-dashed p-12 text-center transition-all cursor-pointer",
        isDragging ? "dragging border-primary bg-primary/10" : "border-border hover:border-muted-foreground",
        disabled && "opacity-50 cursor-not-allowed"
      )}
    >
      <input
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleInputChange}
        disabled={disabled}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
      />
      
      <div className="flex flex-col items-center gap-4">
        <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center">
          {isDragging ? (
            <ImageIcon className="h-8 w-8 text-primary" />
          ) : (
            <Upload className="h-8 w-8 text-muted-foreground" />
          )}
        </div>
        
        <div>
          <p className="text-lg font-medium">
            {isDragging ? 'Drop your image here' : 'Upload your photo'}
          </p>
          <p className="text-sm text-muted-foreground mt-1">
            Drag and drop or click to browse
          </p>
          <p className="text-xs text-muted-foreground mt-2">
            JPG, PNG, or WebP • Max 10MB
          </p>
        </div>
      </div>
      
      {error && (
        <p className="mt-4 text-sm text-destructive">{error}</p>
      )}
    </div>
  )
}

