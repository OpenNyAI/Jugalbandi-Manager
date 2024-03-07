import { ReactNode } from 'react';
import { AuthMS } from './AuthMS';
import { AuthGoogle } from './AuthGoogle';
import { AuthGitHub } from './AuthGithub';

export interface User {
    id: string;
    name:string;
    email:string;
    jb_secret?:string;
}

export type AuthMethodKey = 'MS' | 'GITHUB' | 'GOOGLE';

export interface AuthContextData {
    user?: User;
    logIn: (method: AuthMethodKey, code?:string) => void;
    logOut: () => void;
    isAuthenticated: Boolean;
    getAuthMethodType: () => string;
    getToken: () => Promise<string | undefined>;
    getUser: () => Promise<User | undefined>;
    isLoading: boolean;
}

export const AuthMethod = {
    MS: new AuthMS(),
    GOOGLE: new AuthGoogle(),
    GITHUB: new AuthGitHub()


}

export interface AuthProviderProps {
    children: ReactNode;
}

export interface IAuth {
    type: AuthMethodKey;
    logIn: (code?:string) => Promise<User | void>;
    logOut: () => Promise<void>;
    isAuthenticated: () => Promise<boolean>;
    getToken: () => Promise<string | undefined>;
    getUser: () => Promise<User | undefined>;
}