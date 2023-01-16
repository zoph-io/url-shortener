# 🔗 url-shortener

## 🧠 Rationale

Try out this AWS serverless url-shortener for your own usage and see the benefits it can bring.

It's perfect for shortening links and tracking analytics. Give it a shot and deploy it for your own needs.

Plus, contributions and pull requests are welcome.

## 💡 Features

1. URLs shortener
   1. API (`Create`)
   2. Companion static website
2. Hits counter + Analytics

## 🚀 Usage

### Pre-requirements

1. You will need to have an already issued ACM wildcard Certificate in `us-east-1` AWS region: `*.{your_domain}`
2. Set the proper parameters in the `Makefile`

#### 🎛 Parameters

| Parameters      | Default Value     | Description                                                   |
| --------------- | ----------------- | ------------------------------------------------------------- |
| Product         | `url-shortener`   | Product Name                                                  |
| Project         | `zophio`          | Project Name                                                  |
| Environment     | `dev`             | Environment Name                                              |
| MinChar         | `3`               | Minimum characters for the random shortened link id           |
| MaxChar         | `3`               | Maximum characters for the random shortened link id           |
| Domain          | `zoph.io`         | Desired Domain (must be linked to the HostedZoneId Parameter) |
| SubDomain       | `shortener`       | Desired subdomain of the api                                  |
| HostedZoneId    | `Required`        | Route53 `HostedZoneId` where your domain belongs              |
| FallbackUrl     | `https://zoph.io` | When the url does not exist, fallback url                     |
| CertificateArn  | `Required`        | Arn of the Wildcard ACM Certificate (`us-east-1`)             |
| AWSRegion       | `eu-west-1`       | AWS Region                                                    |
| AlertsRecipient | `Required`        | Email of the recipient of CloudWatch Alarms                   |

### Single Command Deployment

        $ make deploy

### How to shorten urls?

### Using Companion Static Website

Go to the following website after the deployment (depends on your parameters :point_up_2:)

- [https://{SubDomain}.{Domain}]()

#### Using the `Makefile`

        $ make url 'https://google.com'

#### Using `cURL`

```bash
curl -X POST https://{subdomain}.{domain}/create/ \
     --header "Content-Type: application/json" \
     -d '{"long_url": "https://google.com"}'
```

## 📖 Reference

- [Blog post](https://blog.ruanbekker.com/blog/2018/11/30/how-to-setup-a-serverless-url-shortener-with-api-gateway-lambda-and-dynamodb-on-aws/)
- [Makefile](https://itecnote.com/tecnote/r-how-to-pass-argument-to-makefile-from-command-line/)
- [CloudFront Stack](https://github.com/aws-samples/amazon-cloudfront-secure-static-site/tree/master)

## Todo

1. Cleanup Makefile and Readme
2. Handle CSP
3. Handle CORS Properly
4. Re-Deploy from Scratch - Multiple-times
5. Estimate deployment time
6. Add destription to CloudFront Distribution
7. Tags everywhere
