import type { ComfyExtension } from '@comfyorg/comfyui-frontend-types';

export type ReactorNode = Parameters<NonNullable<ComfyExtension['nodeCreated']>>[0];
