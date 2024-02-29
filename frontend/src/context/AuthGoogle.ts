import { AuthMethodKey, IAuth } from './auth.model';
import { googleConfig } from './google.config';
import { loadGapiInsideDOM, loadAuth2WithProps } from 'gapi-script';
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
