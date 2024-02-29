
import { AuthenticationResult, IPublicClientApplication, PublicClientApplication } from '@azure/msal-browser';
import { loginRequest, msalConfig } from './ms.config';
import { AuthMethodKey, IAuth } from './auth.model';

export class AuthMS implements IAuth {

    public type: AuthMethodKey = 'MS';
    private instance: PublicClientApplication;
    
    constructor () {
        this.instance = new PublicClientApplication(msalConfig);
        this.instance.initialize();
    }

    public logIn = async () => {
        await this.instance.handleRedirectPromise().then(() => {
            this.handleLogin(this.instance);
        });
    };


    public logOut = async () => {
        console.log('signOut azure');
        await this.instance.handleRedirectPromise().then(() => {
            this.handleLogout(this.instance);
        });
    };

    public isAuthenticated = async () => {
        return await this.instance.handleRedirectPromise().then(x => {
            const accounts = this.instance.getAllAccounts();
            return accounts.length > 0;
        });
    };


    public getToken = async () => {
        const accounts = this.instance.getAllAccounts();
        if(accounts.length === 0) {
             return undefined;
        }
        const request = {
            ...loginRequest,
            account: accounts[0]
        };
        const response:AuthenticationResult = await this.instance.acquireTokenSilent(request)
        return response.accessToken;
    }
    
        
    private handleLogin = (instance: IPublicClientApplication) => {
        instance.loginRedirect(loginRequest).catch(e => {
            console.error(e);
        });
    }

    private handleLogout = (instance: IPublicClientApplication) => {
        instance.logout().catch(e => {
            console.error(e);
        });
    }
}