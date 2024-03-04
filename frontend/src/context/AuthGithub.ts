import { AuthMethodKey, IAuth } from './auth.model';
import { sendRequest } from '@/api';
const APIHOST = import.meta.env.VITE_SERVER_HOST;

export class AuthGitHub implements IAuth {
    public type: AuthMethodKey = 'GITHUB';
    private accessToken: string | null = null;
    private state: string | null = null;

    constructor() {
        console.log('starting auth GitHub');
        // Optionally, initialize with existing token if available (e.g., from localStorage)
        this.accessToken = localStorage.getItem('github_access_token');
    }

    private generateState(): string {
        const array = new Uint32Array(10);
        window.crypto.getRandomValues(array);
        return Array.from(array, dec => ('0' + dec.toString(16)).substr(-2)).join('');
    }

    public logIn = async (code:string|undefined) => {
        console.log('signIn GitHub');
        if (code) {
            // if (!this.state || !this.verifyState(this.state)) {
            //     throw new Error('Invalid state');
            // }
            await this.exchangeCodeForToken(code);
        } else {
            const clientId =import.meta.env.VITE_GITHUB_CLIENT_ID;
            const scope = 'read:user';
            const redirectUri = encodeURIComponent(import.meta.env.VITE_REDIRECT_URI);
            this.state = this.generateState();
            localStorage.setItem('oauth_state_github', this.state);
            const url = `https://github.com/login/oauth/authorize?client_id=${clientId}&scope=${scope}&redirect_uri=${redirectUri}&state=${this.state}`;
            window.location.href = url;
        }
    };

    public logOut = async () => {
        console.log('signOut GitHub');
        this.accessToken = null;
        localStorage.removeItem('github_access_token'); // Clear the token from storage
    };

    public isAuthenticated = async () => {
        return this.accessToken !== null;
    };

    public getToken = async () => {
        return this.accessToken as string;
    };

    private verifyState(returnedState: string): boolean {
        const storedState = localStorage.getItem('oauth_state_github');
        return storedState === returnedState;
    }

    private async exchangeCodeForToken(code: string): Promise<void> {
        try {
            const response = await sendRequest({
                url: `${APIHOST}/github-auth`,
                body: JSON.stringify({ code }),
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            if (response.access_token) {
                this.accessToken = response.access_token;
                localStorage.setItem('github_access_token', this.accessToken as string);
            }
        } catch (error) {
            
        }
    }
}
