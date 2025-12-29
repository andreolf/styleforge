"use client"

import React from 'react'
import { Check, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'
import { StylePreset } from '@/lib/types'
import { Card, CardContent } from '@/components/ui/card'

interface StyleSelectorProps {
  styles: StylePreset[]
  selectedStyle: string | null
  onSelect: (styleId: string) => void
  disabled?: boolean
}

// Style-specific icons/emojis for visual distinction
const styleIcons: Record<string, string> = {
  'classic-tuxedo': '🎩',
  'streetwear': '👟',
  'techwear': '⚡',
  'old-money': '💎',
  'minimalist': '◽',
  'cyberpunk': '🌆',
  'crypto-bro': '🚀',
}

// Style-specific gradient colors
const styleGradients: Record<string, string> = {
  'classic-tuxedo': 'from-slate-900 to-slate-700',
  'streetwear': 'from-orange-600 to-red-600',
  'techwear': 'from-zinc-800 to-zinc-600',
  'old-money': 'from-amber-700 to-yellow-600',
  'minimalist': 'from-neutral-400 to-neutral-300',
  'cyberpunk': 'from-purple-600 to-pink-500',
  'crypto-bro': 'from-green-500 to-emerald-700',
}

export function StyleSelector({ styles, selectedStyle, onSelect, disabled }: StyleSelectorProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {styles.map((style) => {
        const isSelected = selectedStyle === style.id
        const icon = styleIcons[style.id] || '✨'
        const gradient = styleGradients[style.id] || 'from-primary to-accent'
        
        return (
          <Card
            key={style.id}
            onClick={() => !disabled && onSelect(style.id)}
            className={cn(
              "relative overflow-hidden cursor-pointer transition-all duration-200",
              isSelected 
                ? "ring-2 ring-primary ring-offset-2 ring-offset-background" 
                : "hover:border-muted-foreground",
              disabled && "opacity-50 cursor-not-allowed"
            )}
          >
            {/* Gradient header */}
            <div className={cn(
              "h-20 bg-gradient-to-br flex items-center justify-center",
              gradient
            )}>
              <span className="text-4xl">{icon}</span>
            </div>
            
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold truncate">{style.name}</h3>
                  <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
                    {style.description}
                  </p>
                </div>
                
                {isSelected && (
                  <div className="flex-shrink-0 w-5 h-5 rounded-full bg-primary flex items-center justify-center">
                    <Check className="h-3 w-3 text-primary-foreground" />
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}

