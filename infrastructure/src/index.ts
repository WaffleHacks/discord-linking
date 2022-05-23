import { Client, ResourceServer } from '@pulumi/auth0';
import { getCallerIdentity } from '@pulumi/aws';
import { Policy } from '@pulumi/aws/iam';
import {
  ComponentResource,
  ComponentResourceOptions,
  Input,
  Output,
  ResourceOptions,
  interpolate,
} from '@pulumi/pulumi';

interface Args {
  /**
   * The domain where the service should be accessible
   */
  domain: Input<string>;
  /**
   * The region where the profiles service is deployed
   */
  region: Input<string>;
  /**
   * The API gateway ID for the profiles service
   */
  apiGateway: Input<string>;
}

class DiscordLinking extends ComponentResource {
  public readonly policy: Output<string>;

  public readonly api: Output<string>;

  public readonly clientId: Output<string>;
  public readonly clientSecret: Output<string>;

  constructor(name: string, args: Args, opts?: ComponentResourceOptions) {
    super('wafflehacks:discord-linking:DiscordLinking', name, { options: opts }, opts);

    const defaultResourceOptions: ResourceOptions = { parent: this };
    const { domain, region, apiGateway } = args;

    const api = new ResourceServer(
      `${name}-api`,
      {
        allowOfflineAccess: true,
        name: 'Discord Linking',
        identifier: 'https://discord.wafflehacks.org',
        signingAlg: 'RS256',
        skipConsentForVerifiableFirstPartyClients: true,

        // Enable RBAC
        enforcePolicies: true,
        tokenDialect: 'access_token_authz',
      },
      defaultResourceOptions,
    );
    this.api = api.identifier as Output<string>;

    const urls = [
      'http://127.0.0.1:5000',
      'http://localhost:5000',
      'http://localhost.localdomain:5000',
      interpolate`https://${domain}`,
    ];
    const client = new Client(
      `${name}-client`,
      {
        name: 'Discord Linking',
        appType: 'regular_web',
        isFirstParty: true,
        tokenEndpointAuthMethod: 'client_secret_post',
        grantTypes: ['authorization_code', 'implicit', 'refresh_token', 'client_credentials'],
        jwtConfiguration: {
          alg: 'RS256',
          lifetimeInSeconds: 36000,
          secretEncoded: false,
        },
        oidcConformant: true,
        refreshToken: {
          expirationType: 'expiring',
          leeway: 0,
          tokenLifetime: 2592000,
          idleTokenLifetime: 1296000,
          infiniteTokenLifetime: false,
          infiniteIdleTokenLifetime: false,
          rotationType: 'rotating',
        },

        callbacks: urls.map((u) => interpolate`${u}/auth0/callback`),
        allowedLogoutUrls: urls,
        webOrigins: urls,
      },
      defaultResourceOptions,
    );
    this.clientId = client.clientId;
    this.clientSecret = client.clientSecret;

    const caller = getCallerIdentity();
    const accountId = caller.then((current) => current.accountId);

    const policy = new Policy(
      `${name}-policy`,
      {
        policy: {
          Version: '2012-10-17',
          Statement: [
            {
              Effect: 'Allow',
              Action: ['execute-api:Invoke'],
              Resource: ['manage', 'manage/*'].map(
                (path) => interpolate`arn:aws:execute-api:${region}:${accountId}:${apiGateway}/prod/GET/${path}`,
              ),
            },
          ],
        },
      },
      defaultResourceOptions,
    );

    this.policy = policy.name;
    this.registerOutputs();
  }
}

export default DiscordLinking;
