"use client"

import React from 'react'
import { Loader2, CheckCircle2, XCircle, Clock } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Progress } from '@/components/ui/progress'
import { JobStatus } from '@/lib/types'

interface ProgressIndicatorProps {
  status: JobStatus
  progress: number
  error?: string | null
}

const statusConfig: Record<JobStatus, {
  icon: typeof Loader2
  label: string
  color: string
  animate?: boolean
}> = {
  pending: {
    icon: Clock,
    label: 'Waiting in queue...',
    color: 'text-muted-foreground',
  },
  processing: {
    icon: Loader2,
    label: 'Generating your new look...',
    color: 'text-primary',
    animate: true,
  },
  completed: {
    icon: CheckCircle2,
    label: 'Complete!',
    color: 'text-green-500',
  },
  failed: {
    icon: XCircle,
    label: 'Generation failed',
    color: 'text-destructive',
  },
}

export function ProgressIndicator({ status, progress, error }: ProgressIndicatorProps) {
  const config = statusConfig[status]
  const Icon = config.icon

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="flex flex-col items-center gap-6">
        {/* Icon */}
        <div className={cn(
          "w-16 h-16 rounded-full bg-secondary flex items-center justify-center",
          status === 'processing' && "animate-pulse"
        )}>
          <Icon 
            className={cn(
              "h-8 w-8",
              config.color,
              config.animate && "animate-spin"
            )} 
          />
        </div>

        {/* Status text */}
        <div className="text-center">
          <p className={cn("text-lg font-medium", config.color)}>
            {config.label}
          </p>
          
          {status === 'processing' && (
            <p className="text-sm text-muted-foreground mt-1">
              {progress}% complete
            </p>
          )}
          
          {error && (
            <p className="text-sm text-destructive mt-2">
              {error}
            </p>
          )}
        </div>

        {/* Progress bar */}
        {(status === 'processing' || status === 'pending') && (
          <div className="w-full">
            <Progress value={progress} className="h-2" />
          </div>
        )}

        {/* Processing steps */}
        {status === 'processing' && (
          <div className="flex items-center gap-8 text-xs text-muted-foreground">
            <Step active={progress >= 10} complete={progress >= 30} label="Analyzing" />
            <Step active={progress >= 30} complete={progress >= 70} label="Generating" />
            <Step active={progress >= 70} complete={progress >= 100} label="Finishing" />
          </div>
        )}
      </div>
    </div>
  )
}

function Step({ 
  active, 
  complete, 
  label 
}: { 
  active: boolean
  complete: boolean
  label: string 
}) {
  return (
    <div className={cn(
      "flex items-center gap-2 transition-colors",
      complete ? "text-green-500" : active ? "text-primary" : "text-muted-foreground"
    )}>
      <div className={cn(
        "w-2 h-2 rounded-full",
        complete ? "bg-green-500" : active ? "bg-primary" : "bg-muted"
      )} />
      <span>{label}</span>
    </div>
  )
}

