/*
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License.
 */

/**
 * Makes a GET request using authorization header. For more, visit:
 * https://tools.ietf.org/html/rfc6750
 * @param {string} accessToken 
 * @param {string} apiEndpoint 
 */


export const sendRequest = ({
    url='',
    method="GET",
    accessToken=null,
    body={},
    headers = {},
  }) => {
      const header = new Headers({ ...headers })
      if (accessToken) {
          const bearer = `Bearer ${accessToken}`;
          header.append("Authorization", bearer);
      }
      const options:any = {
          method: method,
          headers: header,// by default setting the content-type to be json type
      };
      if (method.toUpperCase() !== 'GET') {
        if (body instanceof FormData) {
          options.body = body ? body : null
        } else if (body instanceof Object) {
          options.body = (Object.keys(body).length !== 0) ? body : null
        } else {
          options.body = (body) ? body : null
        }
      }
    
  
    return fetch(url, options).then(res => {
      if (res.ok) {
        return res.json();
      } else {
        return res.json().then(function(json) {
          // to be able to access error status when you catch the error 
          return Promise.reject({
            status: res.status,
            ok: false,
            message: json.message,
            body: json
          });
        });
      }
    });
  };
  