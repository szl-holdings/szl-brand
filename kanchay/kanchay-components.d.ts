// SZL Kanchay — window.Kanchay. Types as documentation.
import * as React from "react";

type Tone = "neutral" | "gold" | "good" | "warn" | "bad";
type MarkTone = "gold" | "good" | "warn" | "bad";

/** Gold primary by default. At most one default Button per view. */
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "secondary" | "ghost" | "destructive" | "link";
  size?: "default" | "sm" | "lg" | "icon";
  /** Disables the button and shows a spinner before the label. */
  isLoading?: boolean;
  /** Renders an <a> instead of a <button>. */
  href?: string;
}
export declare const Button: React.ForwardRefExoticComponent<ButtonProps & React.RefAttributes<HTMLButtonElement>>;

export declare const Input: React.ForwardRefExoticComponent<React.InputHTMLAttributes<HTMLInputElement> & React.RefAttributes<HTMLInputElement>>;
export declare const Select: React.ForwardRefExoticComponent<React.SelectHTMLAttributes<HTMLSelectElement> & React.RefAttributes<HTMLSelectElement>>;

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "active" | "running" | "success" | "failed" | "error" | "partial" | "draft" | "paused";
  children: React.ReactNode;
}
export declare function Badge(props: BadgeProps): React.ReactElement;

export interface SeverityChipProps {
  level: "critical" | "high" | "medium" | "low" | "info";
  /** Overrides the default label (CRITICAL, HIGH, MED, LOW, INFO). */
  children?: React.ReactNode;
  className?: string;
}
export declare function SeverityChip(props: SeverityChipProps): React.ReactElement;

export interface GovernanceDotProps {
  state: "green" | "amber" | "red";
  /** Accessible name; defaults to the state. */
  label?: string;
  className?: string;
}
export declare function GovernanceDot(props: GovernanceDotProps): React.ReactElement;

export interface StatusDotProps {
  status?: "ok" | "err" | "loading" | "idle";
  /** Slow 2.2s pulse, for "live" indicators. */
  pulse?: boolean;
  label?: string;
  className?: string;
}
export declare function StatusDot(props: StatusDotProps): React.ReactElement;

export interface FabricStatProps {
  label: React.ReactNode;
  value: React.ReactNode;
  sub?: string;
  tone?: Tone;
  className?: string;
}
export declare function FabricStat(props: FabricStatProps): React.ReactElement;

export interface MicroBarProps { value: number; max?: number; tone?: MarkTone; label?: string; className?: string; }
export declare function MicroBar(props: MicroBarProps): React.ReactElement;

export interface SparklineProps { values: readonly number[]; width?: number; height?: number; tone?: MarkTone; label?: string; className?: string; }
export declare function Sparkline(props: SparklineProps): React.ReactElement;

export interface HeatCellProps { value: number; max: number; className?: string; }
export declare function HeatCell(props: HeatCellProps): React.ReactElement;

export interface OutputPanelProps {
  label?: React.ReactNode;
  status?: "ok" | "err" | "loading" | "idle";
  statusLabel?: string;
  /** Preformatted text. Wrap lines in <span className="kc-ok"> or "kc-deny" to color verdicts. */
  children: React.ReactNode;
  className?: string;
}
export declare function OutputPanel(props: OutputPanelProps): React.ReactElement;

export interface FabricHeaderProps { eyebrow?: string; title: React.ReactNode; blurb?: React.ReactNode; trailing?: React.ReactNode; className?: string; }
export declare function FabricHeader(props: FabricHeaderProps): React.ReactElement;

export interface FabricCardProps { title?: string; trailing?: React.ReactNode; children: React.ReactNode; className?: string; }
export declare function FabricCard(props: FabricCardProps): React.ReactElement;

export declare function Card(props: React.HTMLAttributes<HTMLDivElement>): React.ReactElement;
export declare function CardHeader(props: React.HTMLAttributes<HTMLDivElement>): React.ReactElement;
export declare function CardTitle(props: React.HTMLAttributes<HTMLHeadingElement>): React.ReactElement;
export declare function CardContent(props: React.HTMLAttributes<HTMLDivElement>): React.ReactElement;

export interface FabricToolbarProps { children: React.ReactNode; label?: string; className?: string; }
export declare function FabricToolbar(props: FabricToolbarProps): React.ReactElement;

export interface FabricDrawerProps {
  open: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  /** Mono label above the title. Default "Detail". */
  kicker?: string;
  children: React.ReactNode;
  className?: string;
}
export declare function FabricDrawer(props: FabricDrawerProps): React.ReactElement | null;

export interface SkeletonProps { width?: number | string; height?: number | string; style?: React.CSSProperties; className?: string; }
export declare function Skeleton(props: SkeletonProps): React.ReactElement;

export interface NavItem { name: string; href?: string; icon?: React.ReactNode; active?: boolean; external?: boolean; }
export interface NavSection { label?: string; items: NavItem[]; }
export interface SidebarNavProps {
  brand?: { name: string; letter?: string; href?: string };
  sections: NavSection[];
  collapsed?: boolean;
  defaultCollapsed?: boolean;
  onToggle?: (collapsed: boolean) => void;
  label?: string;
  className?: string;
}
export declare function SidebarNav(props: SidebarNavProps): React.ReactElement;

export interface SiteHeaderProps {
  name?: string;
  tag?: string;
  href?: string;
  /** Defaults to SzlMark; pass false to hide. */
  mark?: React.ReactNode | false;
  cta?: { label: string; href?: string };
  className?: string;
}
export declare function SiteHeader(props: SiteHeaderProps): React.ReactElement;

export interface EyebrowProps { children: React.ReactNode; dot?: boolean; className?: string; }
export declare function Eyebrow(props: EyebrowProps): React.ReactElement;

export interface SzlMarkProps { size?: number; /** Accessible name; "" makes it decorative. */ title?: string; className?: string; style?: React.CSSProperties; }
export declare function SzlMark(props: SzlMarkProps): React.ReactElement;
