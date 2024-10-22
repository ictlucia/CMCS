import ael

# token types
typeString = 'string'
typeInt = 'int'
typeFloat = 'float'
typeChoice = 'choice'
typeTime = 'time'
allTypes = [typeString, typeInt, typeFloat, typeChoice, typeTime]

# tokens
tokenService = 'service'
tokenTranslation = 'translation'
tokenTranslationAPH = 'translationAPH'
tokenSemantics = 'semantics'
tokenPriority = 'priority'
tokenStartTime = 'start_time'
tokenStopTime = 'stop_time'
tokenDigFract = 'dig_fract'
tokenQuoteSize = 'quote_size'
tokenUpdateInterval = 'update_interval'
tokenIgnoreLastInterval = 'ignore_last_interval'
tokenArithmeticA = 'arithmeticA'
tokenArithmeticFactor = 'arithmetic_factor'
tokenIgnoreLastInterval = 'ignore_last_interval'
tokenIgnoreZeroPrice = 'ignore_zero_price'
tokenFunction = 'function'
allTokens = [tokenService, tokenTranslation, tokenTranslationAPH, tokenSemantics, tokenPriority, tokenStartTime,
             tokenStopTime, tokenDigFract, tokenQuoteSize, tokenUpdateInterval, tokenIgnoreLastInterval,
             tokenArithmeticA, tokenArithmeticFactor, tokenIgnoreLastInterval, tokenIgnoreZeroPrice, tokenFunction]

# tokenValidations
# format: token: (prettyName, type, type argument list, exclude list
# type argument list format:
#       typeString: ignored
#       typeInt:    None or [minval, maxval]
#       typeFloat:  None or [minval, maxval]
#       typeChoice: list of valid values, like ['0', '1']
#       typeTime:   ignored
# exclude argument list format: [[type, type argument list], ...]
#   if a value matches a given type but also an exclude type, it will be considered invalid

tokenValidations = {tokenService: ('Service', typeString, None, None),
                    tokenTranslation: ('Translation', typeString, None, None),
                    tokenTranslationAPH: ('Translation APH', typeString, None, [[typeInt, [0, 10000]]]),
                    tokenSemantics: ('Semantics', typeString, None, None),
                    tokenPriority: ('Priority', typeInt, None, None),
                    tokenStartTime: ('Start Time', typeTime, None, None),
                    tokenStopTime: ('Stop Time', typeTime, None, None),
                    tokenDigFract: ('Digital/Fraction', typeChoice, ['D','F'], None),
                    tokenQuoteSize: ('Quote Size', typeFloat, [-1000000000, 1000000000], None),
                    tokenUpdateInterval: ('Update Interval', typeInt, None, None),
                    tokenIgnoreLastInterval: ('Ignore Last Interval', typeChoice, ['0','1'], None),
                    tokenArithmeticA: ('Arithmetic A', typeChoice, ['A'], None),
                    tokenArithmeticFactor: ('Arithmetic Factor', typeFloat, [-1000000000, 1000000000], None),
                    tokenIgnoreLastInterval: ('Ignore Last Interval', typeChoice, ['0','1'], None),
#???            tokenIgnoreZeroPrice: ('Ignore Zero Price', typeChoice, ['0','1'], None),
                    tokenIgnoreZeroPrice: ('Ignore Zero Price', typeString, None, None),
                    tokenFunction: ('Function', typeString, None, None)}

occMandatory = 'mandatory'
occOptional = 'optional'
allOccurences = [occMandatory, occOptional]

# syntax definition
# format: [(token, occurrence), (token, occurrence), ...]

# Valid syntaxes
# If len is 1, it is the RIC
# If len is 2, it is either APH(Service + RIC), or AMPH(RIC + Prio)
# If len is 3 or greater, it is either APH(Service+RIC+Semantics+additional parameters) OR
# .. AMPH(RIC+PRIO+START+additional parameters)

# If len is 1, it is the RIC (don't know if it is for AMPH or APH)
onlyTranslationSyntax = [(tokenTranslation, occMandatory)]

aphShortSyntax = \
    [(tokenService, occMandatory),
    (tokenTranslationAPH, occMandatory)]

'''
aphSyntaxWithService = \
    [(tokenService, occMandatory),
    (tokenTranslationAPH, occMandatory),
    (tokenSemantics, occMandatory),
    (tokenPriority, occOptional),
    (tokenStartTime, occOptional),
    (tokenStopTime, occOptional),
    (tokenDigFract, occOptional),
    (tokenQuoteSize, occOptional),
    (tokenUpdateInterval, occOptional),
    (tokenIgnoreLastInterval, occOptional),
    (tokenArithmeticA, occOptional),
    (tokenArithmeticFactor, occOptional),
    (tokenIgnoreLastInterval, occOptional),
    (tokenIgnoreZeroPrice, occOptional),
    (tokenFunction, occOptional)]
'''

aphSyntax = \
    [(tokenService, occMandatory),
    (tokenTranslationAPH, occMandatory),
    (tokenSemantics, occMandatory),
    (tokenPriority, occOptional),
    (tokenStartTime, occOptional),
    (tokenStopTime, occOptional),
    (tokenDigFract, occOptional),
    (tokenQuoteSize, occOptional),
    (tokenUpdateInterval, occOptional),
    (tokenIgnoreLastInterval, occOptional),
    (tokenArithmeticA, occOptional),
    (tokenArithmeticFactor, occOptional),
    (tokenIgnoreLastInterval, occOptional),
    (tokenIgnoreZeroPrice, occOptional),
    (tokenFunction, occOptional)]

amphShortSyntax = \
    [(tokenTranslation, occMandatory),
    (tokenPriority, occMandatory)]

amphSyntax = \
    [(tokenTranslation, occMandatory),
    (tokenPriority, occMandatory),
    (tokenStartTime, occMandatory),
    (tokenStopTime, occOptional),
    (tokenDigFract, occOptional),
    (tokenQuoteSize, occOptional),
    (tokenUpdateInterval, occOptional),
    (tokenIgnoreLastInterval, occOptional),
    (tokenArithmeticA, occOptional),
    (tokenArithmeticFactor, occOptional),
    (tokenIgnoreLastInterval, occOptional),
    (tokenIgnoreZeroPrice, occOptional),
    (tokenFunction, occOptional)]

# allSyntaxes
# format: [(syntax, prettyName), (syntax, prettyName), ...]

allSyntaxes = [(onlyTranslationSyntax, 'Translation only'),
               (aphShortSyntax, 'APH short'),
               (amphShortSyntax, 'AMPH short'),
               (aphSyntax, 'APH'),
#               (aphSyntaxWithService, 'APH service'),
               (amphSyntax, 'AMPH')]

limitSyntaxes1 = [(aphSyntax, 'APH'),
                 (amphSyntax, 'AMPH')]

limitSyntaxes2 = [(aphShortSyntax, 'APH short'),
               (amphShortSyntax, 'AMPH short')]

limitSyntaxes3 = [(onlyTranslationSyntax, 'Translation only')]

# Validation of the syntaxes and tokens

def validateDataType(dataType, optArgs):
    if dataType == typeChoice:
        if not optArgs:
            raise Exception("Type %s must have an argument list with at least one valid value" % dataType)
        try:
            optArgs[0]
        except:
            raise Exception("Type %s must have an argument list with at least one valid value" % dataType)
    elif dataType == typeInt:
        pass  # todo
    elif dataType == typeFloat:
        pass  # todo
    elif dataType == typeString:
        pass  # todo

def validateTokenValidation(token, prettyName, dataType, optArgs, notTypeEntries):
    global allTokens, allTypes, typeChoice, typeInt, typeFloat

    if not token in allTokens:
        raise Exception("Invalid token, missing in allTokens")
    if not prettyName:
        raise Exception("Nice name missing")
    if not dataType in allTypes:
        raise Exception("Invalid type '%s', missing in allTypes" % dataType)

    validateDataType(dataType, optArgs)

    if notTypeEntries:
        for notEntry in notTypeEntries:
            notEntryLen = len(notEntry)
            notType = None
            notTypeOptArgs = None

            if notEntryLen < 1 or notEntryLen > 2:
                raise Exception("Invalid exclude definition, definition '%s'" % notEntry)
            if notEntryLen > 0:
                notType = notEntry[0]
            if notEntryLen > 1:
                notTypeOptArgs = notEntry[1]

            try:
                validateDataType(notType, notTypeOptArgs)
            except:
                err = "Invalid exclude definition, definition '%s'" % notEntry
                if notTypeOptArgs:
                    err += ", arguments '%s'" % notTypeOptArgs
                raise Exception(err)

def validateSyntax(syntax, name):
    global allTokens, allOccurences, occOptional, occMandatory

    count = 0
    foundOptional = False
    for (token, occ) in syntax:
        if not token:
            raise Exception("Invalid entry in syntax '%s', token missing" % name)
        if not token in allTokens:
            raise Exception("Invalid token '%s' in syntax '%s'" % (token, name))
        if not occ:
            raise Exception("Invalid entry in syntax '%s', occurence missing" % name)
        if not occ in allOccurences:
            raise Exception("Invalid occurence '%s' for token '%s' in syntax '%s'" % (occ, token, name))
        if occ == occOptional and count == 0:
            raise Exception("Invalid occurence '%s' for the first token '%s' in syntax '%s'" % (occ, token, name))
        if occ == occMandatory and foundOptional:
            raise Exception("Invalid occurence '%s' after '%s' for the token '%s' in syntax '%s'" % (occ, occOptional, token, name))
        if occ == occOptional:
            foundOptional = True
        count += 1

    # checks all tokens and syntaxes
def validateSyntaxes():
    global allSyntaxes

    try:
        for key in list(tokenValidations.keys()):
            (prettyName, dataType, optArgs, notEntries) = tokenValidations[key]
            try:
                validateTokenValidation(key, prettyName, dataType, optArgs, notEntries)
                print("Token '%s' OK" % key)
            except Exception as e:
                print("Error in token '%s': %s" % (key, e))
    except Exception as e:
        print("Error when accessing token validations list: %s" % e)

    try:
        for (syntax, name) in allSyntaxes:
            try:
                validateSyntax(syntax, name)
                print("Syntax '%s' OK" % name)
            except Exception as e:
                print("Error in syntax '%s': %s" % (name, e))
    except Exception as e:
        print("Error when accessing syntax list: %s" % e)

# Validation of PriceDefinitions

def matchInt(val, prettyName, optArgs):
    converted = 0
    try:
        converted = int(val)
    except:
        raise Exception("Value '%s' for token '%s' is not an integer" % (val, prettyName))
    if optArgs:
        try:
            if len(optArgs) > 0 and converted < int(optArgs[0]):
                raise Exception("Too small value, %d < %d, for token '%s'" % (converted, int(optArgs[0]), prettyName))
        except:
            raise Exception("optional min argument '%s' is not a number, for token '%s'" % (optArgs[0], prettyName))
        try:
            if len(optArgs) > 1 and converted > int(optArgs[1]):
                raise Exception("Too large value, %d > %d, for token '%s'" % (converted, int(optArgs[1]), prettyName))
        except:
            raise Exception("optional max argument '%s' is not a number, for token '%s'" % (optArgs[1], prettyName))


def matchFloat(val, prettyName, optArgs):
    converted = 0
    try:
        converted = float(val)
    except:
        raise Exception("Value '%s' for token '%s' is not a float" % (val, prettyName))
    if optArgs:
        try:
            if len(optArgs) > 0 and converted < float(optArgs[0]):
                raise Exception("Too small value, %d < %d, for token '%s'" % (converted, float(optArgs[0]), prettyName))
        except:
            raise Exception("optional min argument '%s' is not a number, for token '%s'" % (optArgs[0], prettyName))
        try:
            if len(optArgs) > 1 and converted > float(optArgs[1]):
                raise Exception("Too large value, %d > %d, for token '%s'" % (converted, float(optArgs[1]), prettyName))
        except:
            raise Exception("optional max argument '%s' is not a number, for token '%s'" % (optArgs[1], prettyName))

def matchChoice(val, prettyName, optArgs):
    if optArgs:
        try:
            if not val in optArgs:
                raise Exception("Invalid value '%s' for token '%s', valid values %s" % (val, prettyName, optArgs))
        except:
            raise Exception("List of valid choices missing for token '%s'" % prettyName)
    else:
        raise Exception("List of valid choices missing for token '%s'" % prettyName)

def matchTime(val, prettyName, optArgs):
    valLen = len(val)
    if valLen < 3 or valLen > 4:
        raise Exception("Invalid time '%s' for token '%s', valid formats are HMM and HHMM" % (val, prettyName))

    try:
        matchInt(val, prettyName, None)
    except:
        raise Exception("Invalid time '%s' for token '%s', valid formats are HMM and HHMM" % (val, prettyName))

    try:
        if valLen == 4:
            matchInt(val[0:1], prettyName, [0, 23])
            matchInt(val[2:3], prettyName, [0, 59])
        elif valLen == 3:
            matchInt(val[0:0], prettyName, [0, 2])
            matchInt(val[1:2], prettyName, [0, 59])
    except:
        raise Exception("Invalid time '%s' for token '%s', valid formats are HMM and HHMM" % (val, prettyName))

def matchString(val, prettyName, optArgs):
    pass

def matchToken(val, prettyName, dataType, optArgs, notDataTypes):
    global typeString, typeInt, typeFloat, typeChoice, typeTime

    if dataType == typeString:
        matchString(val, prettyName, optArgs)
    elif dataType == typeInt:
        matchInt(val, prettyName, optArgs)
    elif dataType == typeFloat:
        matchFloat(val, prettyName, optArgs)
    elif dataType == typeChoice:
        matchChoice(val, prettyName, optArgs)
    elif dataType == typeTime:
        matchTime(val, prettyName, optArgs)

    if notDataTypes:
        for notEntry in notDataTypes:
            notEntryLen = len(notEntry)
            notTypeOptArgs = None

            if notEntryLen < 1 or notEntryLen > 2:
                raise Exception("Invalid exclude definition for token '%s', definition '%s'" % (prettyName, notEntry))
            if notEntryLen > 0:
                notType = notEntry[0]
            if notEntryLen > 1:
                notTypeOptArgs = notEntry[1]

            err = ""
            try:
                matchToken(val, "dummy", notType, notTypeOptArgs, None)
                err = "Invalid string '%s' for token '%s', matches exclude type '%s'" % (val, prettyName, notType)
                if notTypeOptArgs:
                    err += " with arguments %s" % notTypeOptArgs
            except:
                # ok, as we should NOT match
                pass

            if err:
                raise Exception(err)

def matchSyntax(syntax, parts, resultList = None):
    global tokenValidations, occMandatory, occOptional

    partIndex = 0
    for (token, occ) in syntax:
        (prettyName, dataType, optArgs, notDataTypes) = tokenValidations[token]

        part = None

        if partIndex < len(parts):
            part = parts[partIndex]
        partIndex += 1


        if occ == occMandatory:
            if not part:
                raise Exception("Mandatory token '%s' missing" % prettyName)
        elif occ == occOptional:
            if not part:
                return
        matchToken(part, prettyName, dataType, optArgs, notDataTypes)
        if resultList is not None:
            resultList.append((prettyName, part));

    if partIndex < len(parts):
        raise Exception("Superfluous data %s" % parts[partIndex:])

def validateLine(lineIn, resultList):
    global allSyntaxes, limitSyntaxes

    line = lineIn
    while line == '!': # Remove the comment
        line = line[1:].strip()

    # A Translation within double quotes and containing spaces is allowed

    # Don't want to use the word Quotation since it is a financial term
    numCitations = line.count('"')
    parts = []
    try:
        if numCitations and numCitations != 2:
            raise Exception("Erroneous citation, %d citation characters" % numCitations)
        elif numCitations == 2:
            first, second, rest = line.split('"')
            if first:
                parts.append(first.strip())
            if second:
                parts.append(second.strip())
            if rest:
                parts.extend(rest.strip().split(' '))
        else: # No quotes, i.e. standard
            line1 = ' '.join(line.split())
            parts = line1.split(' ')
    except:
        raise Exception("Error splitting line '%s'" % lineIn)

    dLen = len(parts)

    if not dLen:
        raise Exception("Empty data line")

    matching = []

    if dLen > 2:
        checkSyntaxes = limitSyntaxes1
    elif dLen > 1:
        checkSyntaxes = limitSyntaxes2
    else:
        checkSyntaxes = limitSyntaxes3


    for (s, name) in checkSyntaxes:
        syntaxResult = []
        try:
            matchSyntax(s, parts, syntaxResult)
            matching.append(name)
            resultList.append((name, "OK", syntaxResult))
        except Exception as e:
            resultList.append((name, str(e), syntaxResult))

    if len(matching) > 0:
        return matching
    raise Exception("Does not match any syntax")


def resultString(pld, lines, resultList):
    defnbr = pld.defnbr
    ins = pld.insaddr.display_id()
    curr = pld.curr.display_id()
    market = pld.source_ptynbr.display_id()

    str = "PriceLinkDefinition"
    if defnbr:
        str += " (%d)" % defnbr
    str += "\n"

    str += "  instrument '%s'\n" % ins
    str += "  currency '%s'\n" % curr
    str += "  market '%s'\n" % market

    if lines:
        for i in range(0, len(lines) - 1):
            str += "  data[%d] '%s'\n" % (i, lines[i])

    if resultList:
        for (name, status, tokens) in resultList:
            str += "    Syntax: '%s', Result: '%s', Matches: %s\n" % (name, status, tokens)

    return str


def raiseResultException(pld, lines, msg, resultList):
    defnbr = pld.defnbr
    ins = pld.insaddr.display_id()
    curr = pld.curr.display_id()
    market = pld.source_ptynbr.display_id()

    err = "Error in PriceLinkDefinition"
    if defnbr:
        err += " (%d)" % defnbr
    err += "\n"

    err += "  instrument '%s'\n" % ins
    err += "  currency '%s'\n" % curr
    err += "  market '%s'\n" % market

    if lines:
        for i in range(0, len(lines) - 1):
            err += "  data[%d] '%s'\n" % (i, lines[i])

    err += "'%s'\n" % msg

    if resultList:
        for (name, status, tokens) in resultList:
            err += "    Syntax: '%s', Result: '%s'\n" % (name, status)
    ael.log(err)
    raise Exception("Unable to commit transaction.(Validation failed)")

def validatePriceLinkDefinition(pld, printResult = False):
    if not pld:
        return

    dataLines = []

    for n in range(0, 3): # Collect data[0], data[1] and data[2]
        try:
            dataLine = getattr(pld, 'data[%d]' % n).strip()
        except:
            raiseResultException(pld, dataLines, "Could not access data[%n]" % n)

        if not dataLine:
            if n == 0:
                raiseResultException(pld, dataLines, "data[0] is empty")
            dataLines.append("")
            continue
        try:
            aiInd = n + 1
            strFieldName = 'PDTrans%dExt' % aiInd

            ai = pld.additional_infos()

            if ai:
                for a in ai:
                    aiSpecs = a.reference_out()
                    for ais in aiSpecs:
                        if ais.record_type == "AdditionalInfoSpec":
                            if  ais.field_name == strFieldName :
                                dataLine += " " # add space so we don't concatenate tokens by mistake
                                dataLine +=  a.value
        except:
            pass # No AddInfoSpec defined on this installation
        dataLines.append(dataLine)


    for n in range(0, len(dataLines)): # Validate data[0], data[1] and data[2]
        if not dataLines[n]:
            continue

        matching = None
        resultList = []
        try:
            matching = validateLine(dataLines[n], resultList)
        except Exception as e:
            raiseResultException(pld, dataLines, str(e), resultList)

        if len(matching) > 1:
            raiseResultException(pld, dataLines, "Ambigous match, data[%d] matches %s" % (n, matching), resultList)

    if printResult:
        print(resultString(pld, dataLines, resultList))



