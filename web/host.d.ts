declare module '*/scripts/app.js' {
  export const app: {
    canvas: { selectedItems?: Set<unknown> };
    ui: { settings: EventTarget };
    extensionManager: { setting: { get(id: string): unknown } };
    registerExtension(extension: {
      name: string;
      init?: () => Promise<void>;
      setup?: () => void | Promise<void>;
      nodeCreated?: (node: import('#web/nodes/contracts.ts').ReactorNode) => void;
      loadedGraphNode?: (node: import('#web/nodes/contracts.ts').ReactorNode) => void;
      getSelectionToolboxCommands?: (item: unknown) => string[];
      commands: Array<{ id: string; label: string; icon?: string; function: () => void }>;
      menuCommands: Array<{ path: string[]; commands: string[] }>;
    }): void;
  };
}

declare module '*/scripts/api.js' {
  export const api: {
    getCustomNodesI18n(): Promise<Record<string, unknown>>;
    fetchApi(route: string, options?: RequestInit): Promise<Response>;
    addEventListener(type: string, listener: (event: Event) => void): void;
  };
}

declare module '*.css' {}
