/** Local ComfyUI routes used by the browser interface. */
export const browserRoutes = {
  settings: {
    status: '/reactor-inc/v1/status',
    values: '/reactor-inc/v1/settings',
    credential: '/reactor-inc/v1/credential',
  },
  live: {
    exchange: '/reactor-inc/v1/live/exchange',
    action: '/reactor-inc/v1/live/action',
    camera: '/reactor-inc/v1/live/camera',
  },
} as const;
