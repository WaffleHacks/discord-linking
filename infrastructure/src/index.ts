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

  constructor(name: string, args: Args, opts?: ComponentResourceOptions) {
    super('wafflehacks:discord-linking:DiscordLinking', name, { options: opts }, opts);

    const defaultResourceOptions: ResourceOptions = { parent: this };
    const { region, apiGateway } = args;

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
