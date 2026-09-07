declare module '*/scripts/app.js' {
  export const app: {
    canvas: { selectedItems?: Set<unknown> };
    registerExtension(extension: {
      name: string;
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
    fetchApi(route: string, options?: RequestInit): Promise<Response>;
    addEventListener(type: string, listener: (event: Event) => void): void;
  };
}

declare module '*.css' {}
