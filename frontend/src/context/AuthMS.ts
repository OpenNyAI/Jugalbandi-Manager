
import { AuthenticationResult, IPublicClientApplication, PublicClientApplication } from '@azure/msal-browser';
import { loginRequest, msalConfig } from './ms.config';
import { AuthMethodKey, IAuth } from './auth.model';
import { sendRequest } from '../api';
const APIHOST = import.meta.env.VITE_SERVER_HOST;


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

    public getUser = async () => {
        const accounts = this.instance.getAllAccounts();
        if (accounts.length === 0) {
            return undefined;
        }
        const request = {
            ...loginRequest,
            account: accounts[0]
        }
        const user = await this.instance.acquireTokenSilent(request).then((response:any) => {
            console.log(response)
            const data = {
                id: response.idTokenClaims.oid,
                email: response.idTokenClaims.preferred_username,
                name: response.idTokenClaims.name,
            }
            return sendRequest({
                url: `${APIHOST}/admin_user`,
                method: 'POST',
                accessToken: response.accessToken,
                loginMethod: this.type.toLowerCase(),
                body: JSON.stringify(data),
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        });
        return user;
    }


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