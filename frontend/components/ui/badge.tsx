import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-storybook-leather text-storybook-cream hover:bg-storybook-leather-dark",
        secondary:
          "border-transparent bg-storybook-gold text-storybook-ink hover:bg-storybook-gold-light",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",
        outline: "text-foreground border-storybook-leather",
        success:
          "border-transparent bg-forest text-white",
        available:
          "border-transparent bg-forest text-white",
        borrowed:
          "border-transparent bg-autumn text-white",
        reserved:
          "border-transparent bg-storybook-purple text-white",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
