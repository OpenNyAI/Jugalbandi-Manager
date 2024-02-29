import { ReactNode } from 'react';
import { AuthMS } from './AuthMS';
import { AuthGoogle } from './AuthGoogle';


export interface User {
    id: string;
    username: string;
    email: string;
    photo?:string;
}

export type AuthMethodKey = 'MS' | 'GITHUB' | 'GOOGLE';

export interface AuthContextData {
    user?: User;
    logIn: (method: AuthMethodKey) => void;
    logOut: () => void;
    isAuthenticated: Boolean;
    getAuthMethodType: () => string;
    getToken: () => Promise<string | undefined>;
}

export const AuthMethod = {
    MS: new AuthMS(),
    GOOGLE: new AuthGoogle(),
    GITHUB: new AuthGoogle()


}

export interface AuthProviderProps {
    children: ReactNode;
}

export interface IAuth {
    type: AuthMethodKey;
    logIn: () => Promise<User | void>;
    logOut: () => Promise<void>;
    isAuthenticated: () => Promise<boolean>;
    getToken: () => Promise<string | undefined>;
}