---
categories: blogg teknik
layout: "details-blog"
published: true
heading: Creating a custom Gatling prococol for AWS Lambda
authors: 
  - bjornbeskow
tags: gatling load test aws lambda kinesis serverless scala
topstory: true
comments: true

---

[Gatling] is a powerful load-testing framework with excellent support for testing http-based applications out of the box (and from version 2.x also with limited support for JMS). While http is enough for many applications, we find a frequent need for using other protocols in addition to http. Gatling has a well designed extension mechanism, which allows you to write your own custom protocol handler to use in your Gatling scenarios. Unfortunately, this mechanism is poorly documented (the 'seminal' work refered to, [GatlingProtocolBreakdown], is from version 1.x). To make things worse, the extension APIs have changed a lot between recent versions. While there are several third party protocol handlers listed in the documentation ([extensions]), all of them are out-of-date and don't work with recent Gatling releases. When looking around, I found two excellent, more recent blog posts that both do a good job in describing the bits and pieces of a Gatling custom protocol ([write-custom-protocol-for-gatling] and [load-testing-zeromq-with-gatling]), but unfortunately they too are out-of-date with the 2.2.x versions.

Since I recently needed a custom protocol to load test a Serverless architecture based on AWS [Lambda] functions and [Kinesis] streams, I had to dig into the API changes to get things working. I ended up reading the source code for the latest version of both the http and jms protocols, in order to understand the APIs. It took me quite a while, so I might as well share my findings!

-[readmore]-

[comment]: # (Links)
[Gatling]: http://gatling.io/
[GatlingProtocolBreakdown]: https://github.com/jagregory/gatling/blob/master/GatlingProtocolBreakdown.md
[extensions]: http://gatling.io/docs/2.2.3/extensions/index.html
[write-custom-protocol-for-gatling]: https://www.trivento.io/write-custom-protocol-for-gatling/
[load-testing-zeromq-with-gatling]: http://mintbeans.com/load-testing-zeromq-with-gatling/
[AWS]: https://aws.amazon.com
[Lambda]: https://aws.amazon.com/lambda
[Kinesis]: https://aws.amazon.com/kinesis
[gatling-aws.git]: https://github.com/callistaenterprise/gatling-aws.git

So here we go: (the complete source code is available at https://github.com/callistaenterprise/gatling-aws.git) Most of the work involved in building a custom Gatling protocol consists of creating the internal DSL used in the Gatling scenario. The DSL for a protocol is typically split in two parts: Configuration of the Protocol, and invoking the protocol Actions and optionally cheking the Action's result. For both the Protocol and the Actions, you need to create a definition of the Protocol and the Actions themselves, as well as a ProtocolBuilder and ActionBuilders to support the DSL for using them. Optionally, you may also want a custom Check and corresponding CheckBuilder to validate the outcome of an Action.

In writing a custom protocol for invoking AWS Lambda functions, we will hence need to define a number of classes:

* AWSProtocol
* AWSProtocolBuilder
* LambdaAction
* LambdaActionBuilder
* LambdaCheck
* LambdaCheckBuilder

Armed with the DSL these classes provide, we should be able to use them in a Gatling test scenario like this:

~~~ Scala
package se.callistaenterprise.awspoc.scenario

import io.gatling.core.Predef._
import se.callistaenterprise.gatling.aws.Predef._

import scala.concurrent.duration._

import com.amazonaws.regions.{Region, Regions}

class LambdaGatlingTest extends Simulation {

  val awsConfig = Aws
    .accessKey("myAccessKey")
    .secretKey("mySecretKey")
    .region(Region.getRegion(Regions.US_EAST_2))
  val lambdaScenario = scenario("Call lambda")
    .exec(
      lambda("myTestGatling").payload("""{"name":"Gatling"}""")
      .check(jsonPath("$[?(@.greeting == 'Hello from Gatling')]"))
    )

  setUp(
    lambdaScenario.inject(atOnceUsers(1))
  ).protocols(awsConfig)
  
}
~~~

Let's begin! We start by defining the Protocol and corresponding ProtocolBuilder. Our protocol should be configured with 3 mandatory properties: accessKey, secretKey and region. These properties should be available for the Action later on. The Protocol looks like this:

~~~ Scala
package se.callistaenterprise.gatling.aws.protocol

import io.gatling.core.CoreComponents
import io.gatling.core.config.{ GatlingConfiguration, Credentials }
import io.gatling.core.protocol.{ ProtocolKey, Protocol }

import com.amazonaws.regions.Region

import akka.actor.ActorSystem

object AwsProtocol {

  val AwsProtocolKey = new ProtocolKey {

    type Protocol = AwsProtocol
    type Components = AwsComponents

    def protocolClass: Class[io.gatling.core.protocol.Protocol] = classOf[AwsProtocol].asInstanceOf[Class[io.gatling.core.protocol.Protocol]]

    def defaultProtocolValue(configuration: GatlingConfiguration): AwsProtocol = throw new IllegalStateException("Can't provide a default value for AwsProtocol")

    def newComponents(system: ActorSystem, coreComponents: CoreComponents): AwsProtocol => AwsComponents = {
      awsProtocol => AwsComponents(awsProtocol)
    }
  }
}

case class AwsProtocol(
    awsAccessKeyId: String,
    awsSecretAccessKey: String,
    awsRegion: Region
) extends Protocol {

  type Components = AwsComponents
}
~~~

In order to make the protocol properties easily accessible for the Action, we wrap them in a Gatling protocol Component:

~~~ Scala
package se.callistaenterprise.gatling.aws.protocol

import io.gatling.core.protocol.ProtocolComponents
import io.gatling.core.session.Session

import akka.actor.ActorRef

case class AwsComponents(awsProtocol: AwsProtocol) extends ProtocolComponents {

  def onStart: Option[Session => Session] = None
  def onExit: Option[Session => Unit] = None
}
~~~

Now that we have the protocol itself defined, we need a ProtocolBuilder to support the DSL for creating and configuring the protocol:

~~~ Scala
package se.callistaenterprise.gatling.aws.protocol

import com.amazonaws.regions.Region

object AwsProtocolBuilderBase {
  def accessKey(accessKey: String) = AwsProtocolBuilderSecretKeyStep(accessKey)
}

case class AwsProtocolBuilderSecretKeyStep(accessKey: String) {
  def secretKey(secretKey: String) = AwsProtocolBuilderRegionStep(accessKey, secretKey)
}

case class AwsProtocolBuilderRegionStep(accessKey: String, secretKey: String) {
  def region(region: Region) = AwsProtocolBuilder(accessKey, secretKey, region)
}

case class AwsProtocolBuilder(accessKey: String, secretKey: String, region: Region) {

  def build = AwsProtocol(
        awsAccessKeyId = accessKey,
        awsSecretAccessKey = secretKey,
        awsRegion = region
  )
}
~~~

The Builder defines the 3 methods that our DSL provides for configuring the Protocol with the parameters for accessKey, secretKey and region. Notice the usage of intermediate classes: We start with the AwsProtocolBuilderBase, and pass through AwsProtocolBuilderSecretKeyStep and AwsProtocolBuilderRegionStep until we land in a fully configured protocol AwsProtocolBuilder. This pattern is typical for creating an internal DSL.

Next, we define the LambdaAction, which performs the actual work. The Action takes a mandatory parameter functionName, an optional payload as paramter for the Lambda function and an optional list of Checks to validate the outcome. The executeOrFail method below is where the Lambda function call is made. 

~~~ Scala
package se.callistaenterprise.gatling.aws.lambda.action

import se.callistaenterprise.gatling.aws.protocol.AwsProtocol
import se.callistaenterprise.gatling.aws.lambda.LambdaCheck

import io.gatling.commons.validation._
import io.gatling.core.action._
import io.gatling.core.check.Check
import io.gatling.core.session.{ Session, Expression }
import io.gatling.core.stats.message.ResponseTimings
import io.gatling.core.stats.StatsEngine
import io.gatling.commons.stats.Status
import io.gatling.core.util.NameGen
import akka.actor.{ ActorRef, ActorSystem, Props }
import akka.util.ByteString

import com.amazonaws.auth.BasicAWSCredentials
import com.amazonaws.regions.{Region, Regions}
import com.amazonaws.services.lambda.AWSLambdaClient
import com.amazonaws.services.lambda.model.InvokeRequest
import com.amazonaws.services.lambda.model.InvokeResult

import java.nio.ByteBuffer

import scala.collection.JavaConverters._

object LambdaAction extends NameGen {

  def apply(functionName: Expression[String], payload: Option[Expression[String]], checks: List[LambdaCheck], protocol: AwsProtocol, system: ActorSystem, statsEngine: StatsEngine, next: Action) = {
    val actor = system.actorOf(LambdaActionActor.props(functionName, payload, checks, protocol, statsEngine, next))
    new ExitableActorDelegatingAction(genName("Lambda"), statsEngine, next, actor)
  }
}

object LambdaActionActor {
  def props(functionName: Expression[String], payload: Option[Expression[String]], checks: List[LambdaCheck], protocol: AwsProtocol, statsEngine: StatsEngine, next: Action): Props =
    Props(new LambdaActionActor(functionName, payload, checks, protocol, statsEngine, next))
}

class LambdaActionActor(
    functionName: Expression[String],
    payload: Option[Expression[String]],
    checks: List[LambdaCheck],
    protocol: AwsProtocol,
    val statsEngine: StatsEngine,
    val next: Action
) extends ActionActor {

  override def execute(session: Session) = {
    val credentials = new BasicAWSCredentials(protocol.awsAccessKeyId, protocol.awsSecretAccessKey)
    val awsClient = new AWSLambdaClient(credentials)
    awsClient.setRegion(protocol.awsRegion)
    val request = new InvokeRequest
    functionName(session).flatMap { resolvedFunctionName =>
      request.setFunctionName(resolvedFunctionName).success
    }
    if (payload.isDefined) {
      payload.get(session).flatMap { resolvePayload =>
        request.setPayload(resolvePayload).success
      }
    }

    var optionalResult : Option[InvokeResult] = None
    var optionalThrowable : Option[Throwable] = None
    
    val startTime = now()
    try {
      optionalResult = Some(awsClient.invoke(request))
    } catch {
      case t: Throwable => optionalThrowable = Some(t)
    }
    val endTime = now()  
    val timings = ResponseTimings(startTime, endTime)
    
    if (optionalThrowable.isEmpty) {
      val result = optionalResult.get
      if (result.getStatusCode >= 200 && result.getStatusCode <= 299) {
        val resultPayload = bytesToString(result.getPayload)
        val (newSession, error) = Check.check(resultPayload, session, checks)
        error match {
          case None                        => {
            statsEngine.logResponse(session, request.getFunctionName(), timings, Status("OK"), None, None)
            next ! newSession(session)
          }
          case Some(Failure(errorMessage)) => {
            statsEngine.logResponse(session, request.getFunctionName(), timings, Status("KO"), None, Some(errorMessage))
            next ! newSession(session).markAsFailed
          }
        }
      } else {
        statsEngine.logResponse(session, request.getFunctionName(), timings, Status("KO"), None, Some(s"Status code ${result.getStatusCode}"))
        next ! session.markAsFailed
      }
    } else {
      val throwable = optionalThrowable.get
      statsEngine.logResponse(session, request.getFunctionName(), timings, Status("KO"), None, Some(throwable.getMessage))
        next ! session.markAsFailed
    }
  }

  @inline
  def bytesToString(buffer: ByteBuffer): String = {
    val bytes = buffer.array()
    return new String(bytes, "UTF-8")
  }

  @inline
  private def now() = System.currentTimeMillis()

}
~~~

The DSL for the LambdaAction is provided by two Builders. LambdaActionBuilder provides access to theprotocol attributes from within the LambdaAction, whereas the LambdaProcessBuilder provides the DSL for configuring an optional argument payload to the Lamdba, and for configuring optional Checks.

~~~ Scala
package se.callistaenterprise.gatling.aws.lambda.action

import se.callistaenterprise.gatling.aws.protocol.{ AwsComponents, AwsProtocol }
import se.callistaenterprise.gatling.aws.lambda.LambdaCheck

import io.gatling.core.action.Action
import io.gatling.core.action.builder.ActionBuilder
import io.gatling.core.config.GatlingConfiguration
import io.gatling.core.protocol.ProtocolComponentsRegistry
import io.gatling.core.session.Expression
import io.gatling.core.structure.ScenarioContext

case class LambdaActionBuilder(functionName: Expression[String], payload: Option[Expression[String]], checks: List[LambdaCheck]) extends ActionBuilder {

  private def components(protocolComponentsRegistry: ProtocolComponentsRegistry): AwsComponents =
    protocolComponentsRegistry.components(AwsProtocol.AwsProtocolKey)

  override def build(ctx: ScenarioContext, next: Action): Action = {
    import ctx._
    val statsEngine = coreComponents.statsEngine
    val awsComponents = components(protocolComponentsRegistry)
    LambdaAction(functionName, payload, checks, awsComponents.awsProtocol, ctx.system, statsEngine, next)
  }

}
~~~

~~~ Scala
package se.callistaenterprise.gatling.aws.lambda.process

import se.callistaenterprise.gatling.aws.lambda.action.LambdaActionBuilder
import se.callistaenterprise.gatling.aws.lambda.LambdaCheck
import se.callistaenterprise.gatling.aws.lambda.check.LambdaCheckSupport
import io.gatling.core.action.builder.ActionBuilder
import io.gatling.core.session.Expression

case class LambdaProcessBuilder(functionName: Expression[String], payload: Option[Expression[String]] = None, checks: List[LambdaCheck] = Nil) extends LambdaCheckSupport {
  /**
   * Set payload.
   */
  def payload(payload: Expression[String]) = copy(payload = Some(payload))

    /**
   * Add a check that will be perfomed on the response payload before giving Gatling on OK/KO response
   */
  def check(lambdaChecks: LambdaCheck*) = copy(checks = checks ::: lambdaChecks.toList)

  def build(): ActionBuilder = LambdaActionBuilder(functionName, payload, checks)
}
~~~

Note how the LambdaProcessBuilder uses copy() to implement the optional payload and checks, since the LambdaProcessBuilder itself is immutable. If an optional payload is provided, we create a copy of the builder with the optional parameter set.

We also need to define the Checks classes to support validating the Lambda function result. All checks operate on the resulting payload as a String:

~~~ Scala
package se.callistaenterprise.gatling.aws

import io.gatling.core.check.{ Check, Preparer, Extender }
import io.gatling.commons.validation.Success

package object lambda {

  /**
   * Type for Lambda checks
   */
  type LambdaCheck = Check[String]
  
  val LambdaStringExtender: Extender[LambdaCheck, String] = 
     (check: LambdaCheck) => check
  
  val LambdaStringPreparer: Preparer[String, String] = 
     (result: String) => Success(result)
  
}
~~~ 

The Extender and Preparer functions are required by the Gatling base check support.

We support validating the Lambda executing result using a Regex, an XPath or JsonPath expression or by providing a custom function.

~~~ Scala
package se.callistaenterprise.gatling.aws.lambda.check

import se.callistaenterprise.gatling.aws.lambda._

import io.gatling.core.check.DefaultMultipleFindCheckBuilder
import io.gatling.core.check.extractor.regex._
import io.gatling.core.session.{ Expression, RichExpression }

import com.amazonaws.services.lambda.model.InvokeResult

trait LambdaRegexOfType { self: LambdaRegexCheckBuilder[String] =>

  def ofType[X: GroupExtractor](implicit extractorFactory: RegexExtractorFactory) = new LambdaRegexCheckBuilder[X](expression)
}

object LambdaRegexCheckBuilder {

  def regex(expression: Expression[String])(implicit extractorFactory: RegexExtractorFactory) =
    new LambdaRegexCheckBuilder[String](expression) with LambdaRegexOfType
}

class LambdaRegexCheckBuilder[X: GroupExtractor](private[check] val expression: Expression[String])(implicit extractorFactory: RegexExtractorFactory)
    extends DefaultMultipleFindCheckBuilder[LambdaCheck, String, CharSequence, X](LambdaStringExtender, LambdaStringPreparer) {
  import extractorFactory._

  def findExtractor(occurrence: Int) = expression.map(newSingleExtractor[X](_, occurrence))
  def findAllExtractor = expression.map(newMultipleExtractor[X])
  def countExtractor = expression.map(newCountExtractor)
}
~~~

~~~ Scala
package se.callistaenterprise.gatling.aws.lambda.check

import java.io.StringReader

import io.gatling.commons.validation._
import io.gatling.core.check._
import io.gatling.core.check.extractor.xpath._

import org.xml.sax.InputSource

import se.callistaenterprise.gatling.aws.lambda._

object LambdaXPathCheckBuilder extends XPathCheckBuilder[LambdaCheck, String] {

  private val ErrorMapper: String => String = "Could not parse response into a DOM Document: " + _

  def preparer[T](f: InputSource => T)(payload: String): Validation[Option[T]] =
    safely(ErrorMapper) {
      Some(f(new InputSource(new StringReader(payload)))).success
    }

  val CheckBuilder: Extender[LambdaCheck, String] = (wrapped: LambdaCheck) => wrapped
}
~~~ 

~~~ Scala
package se.callistaenterprise.gatling.aws.lambda.check

import se.callistaenterprise.gatling.aws.lambda._

import io.gatling.core.check.{ DefaultMultipleFindCheckBuilder, Preparer }
import io.gatling.core.check.extractor.jsonpath._
import io.gatling.core.json.JsonParsers
import io.gatling.core.session.{ Expression, RichExpression }

trait LambdaJsonPathOfType {
  self: LambdaJsonPathCheckBuilder[String] =>

  def ofType[X: JsonFilter](implicit extractorFactory: JsonPathExtractorFactory) = new LambdaJsonPathCheckBuilder[X](path, jsonParsers)
}

object LambdaJsonPathCheckBuilder {

  val CharsParsingThreshold = 200 * 1000
  
  def preparer(jsonParsers: JsonParsers): Preparer[String, Any] =
    response => {
      if (response.length() > CharsParsingThreshold || jsonParsers.preferJackson)
        jsonParsers.safeParseJackson(response)
      else
        jsonParsers.safeParseBoon(response)
    }

  def jsonPath(path: Expression[String])(implicit extractorFactory: JsonPathExtractorFactory, jsonParsers: JsonParsers) =
    new LambdaJsonPathCheckBuilder[String](path, jsonParsers) with LambdaJsonPathOfType
}

class LambdaJsonPathCheckBuilder[X: JsonFilter](
  private[check] val path:        Expression[String],
  private[check] val jsonParsers: JsonParsers
)(implicit extractorFactory: JsonPathExtractorFactory)
    extends DefaultMultipleFindCheckBuilder[LambdaCheck, String, Any, X](
      LambdaStringExtender,
      LambdaJsonPathCheckBuilder.preparer(jsonParsers)
    ) {

  import extractorFactory._

  def findExtractor(occurrence: Int) = path.map(newSingleExtractor[X](_, occurrence))
  def findAllExtractor = path.map(newMultipleExtractor[X])
  def countExtractor = path.map(newCountExtractor)
}
~~~

~~~ Scala
package se.callistaenterprise.gatling.aws.lambda.check

import scala.collection.mutable

import io.gatling.commons.validation._
import io.gatling.core.check.CheckResult
import io.gatling.core.session.Session
import se.callistaenterprise.gatling.aws.lambda._

case class LambdaCustomCheck(func: String => Boolean) extends LambdaCheck {
  override def check(response: String, session: Session)(implicit cache: mutable.Map[Any, Any]): Validation[CheckResult] = {
    func(response) match {
      case true => CheckResult.NoopCheckResultSuccess
      case _    => Failure("Lambda check failed")
    }
  }
}
~~~

We also provide a supporting trait LambdaCheckSupport for the DSL to construct and configure the checks:

~~~ Scala
package se.callistaenterprise.gatling.aws.lambda.check

import io.gatling.core.session.Expression
import io.gatling.core.check.extractor.regex._
import io.gatling.core.check.extractor.jsonpath.JsonPathExtractorFactory
import io.gatling.core.check.extractor.xpath.{ JdkXPathExtractorFactory, SaxonXPathExtractorFactory }
import io.gatling.core.json.JsonParsers

trait LambdaCheckSupport {

  def regex(expression: Expression[String])(implicit extractorFactory: RegexExtractorFactory) =
    LambdaRegexCheckBuilder.regex(expression)

  def xpath(expression: Expression[String], namespaces: List[(String, String)] = Nil)(implicit extractorFactory: SaxonXPathExtractorFactory, jdkXPathExtractorFactory: JdkXPathExtractorFactory) =
    LambdaXPathCheckBuilder.xpath(expression, namespaces)

  def jsonPath(path: Expression[String])(implicit extractorFactory: JsonPathExtractorFactory, jsonParsers: JsonParsers) =
    LambdaJsonPathCheckBuilder.jsonPath(path)

  def customCheck = LambdaCustomCheck
  
}
~~~

Finally, we define a trait AwsDsl to provide the toplevel DSL builder object (Aws), as well as a DSL builder method lambda for the action:

~~~ Scala
package se.callistaenterprise.gatling.aws

import se.callistaenterprise.gatling.aws.lambda.process.LambdaProcessBuilder
import se.callistaenterprise.gatling.aws.lambda.check.LambdaCheckSupport
import se.callistaenterprise.gatling.aws.protocol.{ AwsProtocol, AwsProtocolBuilder, AwsProtocolBuilderBase }
import io.gatling.core.action.builder.ActionBuilder

import scala.language.implicitConversions

trait AwsDsl extends LambdaCheckSupport {

  val Aws = AwsProtocolBuilderBase

  def lambda(functionName: String) = LambdaProcessBuilder(functionName)

  implicit def awsProtocolBuilder2awsProtocol(builder: AwsProtocolBuilder): AwsProtocol = builder.build
  implicit def lambdaProcessBuilder2ActionBuilder(builder: LambdaProcessBuilder): ActionBuilder = builder.build()

}
~~~

~~~ Scala
package se.callistaenterprise.gatling.aws

object Predef extends AwsDsl
~~~

And we're done. Not as simple as I thought when I started, but quite doable. The documentation for the Gatling extension mechanism could definitely be better, but it is extremely powerful once you understand it. I hope this article can be useful for others. You can find the full source code here: 

https://github.com/callistaenterprise/gatling-aws.git.
