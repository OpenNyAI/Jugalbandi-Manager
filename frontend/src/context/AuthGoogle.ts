import { AuthMethodKey, IAuth } from './auth.model';
import { googleConfig } from './google.config';
import { loadGapiInsideDOM, loadAuth2WithProps } from 'gapi-script';
import { sendRequest } from '../api';
const APIHOST = import.meta.env.VITE_SERVER_HOST;
//global gapi

export class AuthGoogle implements IAuth {
    public type: AuthMethodKey = 'GOOGLE';
    private instance: gapi.auth2.GoogleAuth | undefined;

    constructor(){
        console.log('starting auth google');
        this.initialize();
    }

    public logIn = async () => {
        console.log('signIn google');
        if(!this.instance) await this.initialize();
        this.instance?.signIn();
    };

    public logOut = async () => {
        console.log('signOut google');
        if(!this.instance) await this.initialize();
        this.instance?.signOut();
    };

    public isAuthenticated = async () => {
        if(!this.instance) await this.initialize();
        return this.instance?.isSignedIn.get();
    };

    public getUser = async () => {
        if(!this.instance) await this.initialize();
        const googleUser = this.instance?.currentUser.get();
        console.log(googleUser.getBasicProfile())
        const data = {
            id: googleUser.getBasicProfile().getId(),
            email: googleUser.getBasicProfile().getEmail(),
            name: googleUser.getBasicProfile().getName(),
        }
        return sendRequest({
            url: `${APIHOST}/admin_user`,
            method: 'POST',
            accessToken: googleUser.xc?.access_token,
            loginMethod: this.type.toLowerCase(),
            onUnauthorized: this.logOut,
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    public getToken = async () => {
        if(!this.instance) await this.initialize();
        const googleUser = this.instance?.currentUser.get();
        return googleUser.xc?.access_token;
    }

    private initialize = async () => {
        await loadGapiInsideDOM();
        this.instance = await loadAuth2WithProps(gapi, googleConfig);
    };
}
