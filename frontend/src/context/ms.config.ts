
interface MsalConfig {
    auth: {
      clientId: string,
      redirectUri: string,
      authority: string,
    },
    cache: {
      cacheLocation: string,
      storeAuthStateInCookie: boolean,
    }
  }
  
  export const msalConfig = {
      auth: {
        clientId: import.meta.env.VITE_MS_CLIENT_ID,
        redirectUri: import.meta.env.VITE_REDIRECT_URI,
        authority: `https://login.microsoftonline.com/${import.meta.env.VITE_MS_TENANT_ID}`
      },
      cache: {
        cacheLocation: 'sessionStorage',
        storeAuthStateInCookie: false,
      },
  } as MsalConfig;
    
  export const loginRequest = {
    scopes: [import.meta.env.VITE_MS_SCOPE_URI],
  }
  