export type NodeWidget = {
  name: string;
  label?: string;
  value: unknown;
  advanced?: boolean;
  options?: { values?: string[]; advanced?: boolean };
};
export type ReactorNode = {
  comfyClass?: string;
  widgets?: NodeWidget[];
  inputs?: Array<{ name: string; link?: number | null }>;
  addWidget(
    type: string,
    name: string,
    value: string,
    callback: () => void,
    options: { serialize: boolean },
  ): NodeWidget;
  onRemoved?: (...args: unknown[]) => void;
  onConnectionsChange?: (...args: unknown[]) => void;
  graph?: { setDirtyCanvas(foreground: boolean): void };
};
